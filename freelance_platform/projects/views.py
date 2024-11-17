from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, ReviewForm
from django.shortcuts import get_object_or_404
from .forms import ApplicationForm
from .forms import ProjectCreationForm
from django.contrib.auth.decorators import login_required
from .models import Project, Application, Report
from django.shortcuts import render, redirect
from .forms import ReportForm
from .notifications import *


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически входим после регистрации
            login(request, user)
            # Перенаправляем на соответствующую страницу
            if user.role == 'employer':
                return redirect('employer_dashboard')
            else:
                return redirect('freelancer_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if send_contact_form_notification(name, email, message):
            messages.success(request, 'Ваше сообщение успешно отправлено!')
        else:
            messages.error(request, 'Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.')

        return redirect('contacts')

    return render(request, 'contacts.html')


# Для внештатной ситуации
def home(request):
    return render(request, 'home.html')


@login_required
def redirect_after_login(request):
    user = request.user
    if user.role == 'freelancer':
        return redirect('freelancer_dashboard')
    elif user.role == 'employer':
        return redirect('my_projects')
    else:
        return redirect('home')  # На случай, если роль не определена


@login_required
def employer_dashboard(request):
    if request.user.role != 'employer':
        return redirect('home')

    projects = Project.objects.filter(employer=request.user)

    sort_param = request.GET.get('sort')
    if sort_param:
        if sort_param == 'title':
            projects = projects.order_by('title')
        elif sort_param == 'budget':
            projects = projects.order_by('budget')
        elif sort_param == 'deadline':
            projects = projects.order_by('deadline')
        elif sort_param == 'status':
            projects = projects.order_by('status')

    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.employer = request.user
            project.save()
            messages.success(request, 'Проект успешно создан!')
            return redirect('my_projects')
    else:
        form = ProjectCreationForm()

    return render(request, 'employer_dashboard.html', {'projects': projects, 'form': form})


@login_required
def freelancer_dashboard(request):
    if request.user.role != 'freelancer':
        return redirect('home')

    # Получаем параметры сортировки
    sort_param = request.GET.get('sort')
    applied_sort_param = request.GET.get('applied_sort')

    # Доступные проекты (на которые фрилансер еще не подал заявку)
    available_projects = Project.objects.filter(status='open').exclude(application__freelancer=request.user)

    # Сортировка доступных проектов
    if sort_param:
        if sort_param == 'title':
            available_projects = available_projects.order_by('title')
        elif sort_param == 'budget':
            available_projects = available_projects.order_by('budget')
        elif sort_param == 'deadline':
            available_projects = available_projects.order_by('deadline')
        elif sort_param == 'status':
            available_projects = available_projects.order_by('status')

    # Проекты, на которые фрилансер уже подал заявку
    applied_projects = Project.objects.filter(application__freelancer=request.user)

    # Получаем все заявки фрилансера для отображения их статусов
    applications = Application.objects.filter(freelancer=request.user)

    # Сортировка проектов с заявками
    if applied_sort_param:
        if applied_sort_param == 'title':
            applied_projects = applied_projects.order_by('title')
        elif applied_sort_param == 'budget':
            applied_projects = applied_projects.order_by('budget')
        elif applied_sort_param == 'deadline':
            applied_projects = applied_projects.order_by('deadline')
        elif applied_sort_param == 'status':
            applied_projects = applied_projects.order_by('status')

    return render(request, 'freelancer_dashboard.html', {
        'available_projects': available_projects,
        'applied_projects': applied_projects,
        'applications': applications,
    })


@login_required
def apply_for_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.freelancer = request.user
            application.project = project
            application.save()

            # Отправляем уведомление работодателю о новой заявке
            send_new_application_notification(application)

            return redirect('freelancer_dashboard')

    else:
        form = ApplicationForm()

    return render(request, 'apply_for_project.html', {'form': form, 'project': project})


@login_required
def upload_report(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Удаляем предыдущий отчет, если он существует
            Report.objects.filter(
                project=application.project,
                freelancer=request.user
            ).delete()

            # Создаем новый отчет
            report = form.save(commit=False)
            report.freelancer = request.user
            report.project = application.project
            report.save()

            # Обновляем статус заявки
            application.status = 'submitted'
            application.save()

            messages.success(request, 'Отчет успешно отправлен!')
            return redirect('my_applications')
    else:
        form = ReportForm()

    return render(request, 'upload_report.html', {
        'form': form,
        'application': application
    })


@login_required
def complete_project(request, application_id):
    # Получаем заявку по ID и проверяем, что проект принадлежит текущему работодателю
    application = get_object_or_404(Application, id=application_id, project__employer=request.user)

    # Проверяем, что заявка находится в статусе 'submitted'
    if application.status != 'submitted':
        return redirect('employer_dashboard')

    if request.method == 'POST':
        # Обновляем статус заявки на 'completed'
        application.status = 'completed'
        application.save()

        # Обновляем статус проекта на 'completed'
        project = application.project
        project.status = 'completed'
        project.save()

        return redirect('employer_dashboard')

    return render(request, 'complete_project.html', {'application': application})


@login_required
def review_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    application = Application.objects.get(project=report.project, freelancer=report.freelancer)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            # Принятие отчета
            report.status = 'accepted'
            report.save()
            # Обновляем статус заявки на "отчет принят"
            application.status = 'report_accepted'
            application.save()
            # Завершаем проект
            report.project.status = 'completed'
            report.project.save()
            # Отправляем письмо
            send_report_accepted_notification(report)

        elif action == 'reject':
            # Отклонение отчета
            report.status = 'rejected'
            report.save()
            # Обновляем статус заявки на "отчет отклонен"
            application.status = 'report_rejected'
            application.save()
            # Проект остается в работе
            report.project.status = 'in_progress'
            report.project.save()
            # Отправляем письмо
            send_report_rejected_notification(report)

        return redirect('view_applications', project_id=report.project.id)

    return render(request, 'review_report.html', {'report': report})


@login_required
def view_applications(request, project_id):
    # Получаем проект работодателя
    project = get_object_or_404(Project, id=project_id, employer=request.user)

    # Получаем все заявки на этот проект
    applications = Application.objects.filter(project=project)

    # Добавляем сортировку
    sort_param = request.GET.get('sort')
    if sort_param:
        if sort_param == 'freelancer':
            applications = applications.order_by('freelancer__username')
        elif sort_param == 'price':
            applications = applications.order_by('price_offer')
        elif sort_param == 'status':
            applications = applications.order_by('status')

    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')  # Определяем действие: принять или отклонить
        application = get_object_or_404(Application, id=application_id)

        if action == 'accept':
            application.status = 'accepted'
            project.status = 'in_progress'  # Обновляем статус проекта на "В работе"
            project.save()
        elif action == 'reject':
            application.status = 'rejected'

        application.save()

    return render(request, 'view_applications.html', {'project': project, 'applications': applications})


@login_required
def my_projects(request):
    sort_param = request.GET.get('sort')
    projects = Project.objects.filter(employer=request.user)

    if sort_param:
        if sort_param == 'title':
            projects = projects.order_by('title')
        elif sort_param == 'budget':
            projects = projects.order_by('budget')
        elif sort_param == 'deadline':
            projects = projects.order_by('deadline')
        elif sort_param == 'status':
            projects = projects.order_by('status')

    return render(request, 'my_projects.html', {
        'projects': projects
    })


@login_required
def my_applications(request):
    # Получаем параметр сортировки
    sort_param = request.GET.get('sort')

    # Получаем все заявки текущего фрилансера
    applications = Application.objects.filter(freelancer=request.user)

    # Получаем все проекты, на которые поданы заявки
    applied_projects = Project.objects.filter(application__in=applications)

    # Применяем сортировку
    if sort_param:
        if sort_param == 'title':
            applied_projects = applied_projects.order_by('title')
        elif sort_param == 'budget':
            applied_projects = applied_projects.order_by('budget')
        elif sort_param == 'deadline':
            applied_projects = applied_projects.order_by('deadline')
        elif sort_param == 'status':
            applied_projects = applied_projects.order_by('application__status')

    return render(request, 'my_applications.html', {
        'applications': applications,
        'applied_projects': applied_projects,
    })


@login_required
def submit_review(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.project = project
            review.save()
            return redirect('freelancer_dashboard')

    else:
        form = ReviewForm()

    return render(request, 'submit_review.html', {'form': form})


@login_required
def cancel_application(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    application = get_object_or_404(Application, project=project, freelancer=request.user)

    # Удаляем заявку
    if request.method == 'POST':
        application.delete()
        return redirect('freelancer_dashboard')

    return render(request, 'cancel_application.html', {'project': project})


@login_required
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    project = application.project

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            # Отклоняем все остальные заявки и помечаем для них проект как закрытый
            other_applications = Application.objects.filter(project=project).exclude(id=application_id)
            for other_app in other_applications:
                other_app.status = 'rejected_final'
                other_app.project.status = 'closed'  # Для отклоненных заявок проект помечается как закрытый
                other_app.save()

            # Принимаем выбранную заявку
            application.status = 'accepted'
            application.save()

            # Для принятой заявки проект помечается как "в работе"
            project.status = 'in_progress'
            project.save()

            # Отправляем письмо
            send_application_accepted_notification(application)

        elif action == 'reject':
            application.status = 'rejected'
            application.save()

            # Отправляем письмо
            send_application_rejected_notification(application)

        return redirect('view_applications', project_id=project.id)

    return render(request, 'application_detail.html', {
        'application': application,
        'project': project
    })


@login_required
def cancel_project(request, project_id):
    # Получаем проект по ID и проверяем, что он принадлежит текущему пользователю (работодателю)
    project = get_object_or_404(Project, id=project_id, employer=request.user)

    if request.method == 'POST':
        # Удаляем проект только если он еще не завершен
        if project.status != 'completed':
            project.delete()
            return redirect('my_projects')

    return render(request, 'cancel_project.html', {'project': project})


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    applications = project.application_set.all()

    # Проверяем, есть ли принятая заявка
    accepted_application = applications.filter(status__in=['accepted', 'report_accepted']).first()

    # Проверяем, был ли отправлен отчет
    submitted_application = applications.filter(status__in=['submitted', 'report_rejected']).first()

    if submitted_application:
        # Если отчет отправлен, показываем информацию о фрилансере и статусе отчета
        report = Report.objects.filter(
            project=project,
            freelancer=submitted_application.freelancer
        ).first()

        context = {
            'project': project,
            'freelancer': submitted_application.freelancer,
            'application': submitted_application,
            'application_status': submitted_application.get_status_display(),
            'report': report,
        }
        return render(request, 'project_assigned.html', context)

    elif accepted_application:
        # Если есть принятая заявка, но отчет еще не отправлен
        report = Report.objects.filter(
            project=project,
            freelancer=accepted_application.freelancer
        ).first()

        context = {
            'project': project,
            'freelancer': accepted_application.freelancer,
            'application': accepted_application,
            'application_status': accepted_application.get_status_display(),
            'report': report,
        }
        return render(request, 'project_assigned.html', context)

    else:
        # Если нет принятой заявки, показываем список заявок
        context = {
            'project': project,
            'applications': applications,
        }
        return render(request, 'view_project.html', context)


@login_required
def delete_application(request, application_id):
    # Получаем заявку по ID и проверяем, что она принадлежит текущему фрилансеру
    application = get_object_or_404(Application, id=application_id, freelancer=request.user)
    project = application.project

    if request.method == 'POST':
        # Удаляем заявку
        application.delete()

        # Проверяем статус проекта: если проект еще открыт (актуален), возвращаем его в доступные проекты
        if project.status == 'open':
            return redirect('freelancer_dashboard')  # Фрилансер увидит проект снова в доступных проектах

    return redirect('freelancer_dashboard')


@login_required
def retry_application(request, application_id):
    old_application = get_object_or_404(Application, id=application_id)

    # Проверяем, не выбран ли уже исполнитель
    if Application.objects.filter(
            project=old_application.project,
            status='accepted'
    ).exists():
        messages.error(request, 'Невозможно подать заявку. Проект уже имеет исполнителя.')
        return redirect('freelancer_dashboard')

    if request.method == 'POST':
        # Получаем существующую заявку
        application = get_object_or_404(Application, id=application_id)

        # Обновляем данные существующей заявки
        application.price_offer = request.POST.get('price_offer')
        application.experience_description = request.POST.get('experience_description')
        application.status = 'pending'  # Меняем статус обратно на "на рассмотрении"
        application.save()

        # Отправляем уведомление работодателю о новой заявке
        send_new_application_notification(application)

        return redirect('freelancer_dashboard')

    return redirect('home')
