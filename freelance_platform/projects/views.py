from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, ReviewForm
from django.shortcuts import get_object_or_404
from .forms import ApplicationForm
from .forms import ProjectCreationForm
from django.contrib.auth.decorators import login_required
from .models import Project, Application


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def create_project(request):
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.employer = request.user  # Назначаем работодателя текущему пользователю.
            project.save()
            return redirect('project_list')
    else:
        form = ProjectCreationForm()

    return render(request, 'create_project.html', {'form': form})


def apply_for_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.freelancer = request.user  # Назначаем фрилансера текущему пользователю.
            application.project = project  # Привязываем заявку к проекту.
            application.save()
            return redirect('project_detail', project_id=project.id)

    else:
        form = ApplicationForm()

    return render(request, 'apply_for_project.html', {'form': form})


# Стартовая страница
def home(request):
    return render(request, 'home.html')


@login_required
def redirect_after_login(request):
    user = request.user
    if user.role == 'freelancer':
        return redirect('freelancer_dashboard')
    elif user.role == 'employer':
        return redirect('employer_dashboard')
    else:
        return redirect('home')  # На случай, если роль не определена


@login_required
def employer_dashboard(request):
    if request.user.role != 'employer':
        return redirect('home')

    projects = Project.objects.filter(employer=request.user)

    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.employer = request.user
            project.save()
            return redirect('employer_dashboard')
    else:
        form = ProjectCreationForm()

    return render(request, 'employer_dashboard.html', {'projects': projects, 'form': form})


@login_required
def freelancer_dashboard(request):
    if request.user.role != 'freelancer':
        return redirect('home')

    # Доступные проекты (на которые фрилансер еще не подал заявку)
    available_projects = Project.objects.filter(status='open').exclude(application__freelancer=request.user)

    # Проекты, на которые фрилансер уже подал заявку
    applied_projects = Project.objects.filter(application__freelancer=request.user)

    # Получаем все заявки фрилансера для отображения их статусов
    applications = Application.objects.filter(freelancer=request.user)

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
            return redirect('freelancer_dashboard')

    else:
        form = ApplicationForm()

    return render(request, 'apply_for_project.html', {'form': form, 'project': project})


@login_required
def upload_report(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.freelancer = request.user
            report.project = project
            report.save()
            return redirect('freelancer_dashboard')

    else:
        form = ReportForm()

    return render(request, 'upload_report.html', {'form': form})


@login_required
def view_applications(request, project_id):
    # Получаем проект работодателя
    project = get_object_or_404(Project, id=project_id, employer=request.user)

    # Получаем все заявки на этот проект
    applications = Application.objects.filter(project=project)

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
    # Получаем заявку по ID и проверяем, что проект принадлежит текущему работодателю
    application = get_object_or_404(Application, id=application_id, project__employer=request.user)

    return render(request, 'application_detail.html', {'application': application})


@login_required
def cancel_project(request, project_id):
    # Получаем проект по ID и проверяем, что он принадлежит текущему пользователю (работодателю)
    project = get_object_or_404(Project, id=project_id, employer=request.user)

    if request.method == 'POST':
        # Удаляем проект только если он еще не завершен
        if project.status != 'completed':
            project.delete()
            return redirect('employer_dashboard')

    return render(request, 'cancel_project.html', {'project': project})


@login_required
def project_detail(request, project_id):
    # Получаем проект по ID и проверяем, что он принадлежит текущему работодателю
    project = get_object_or_404(Project, id=project_id, employer=request.user)

    # Получаем все заявки на этот проект
    applications = Application.objects.filter(project=project)

    return render(request, 'view_project.html', {'project': project, 'applications': applications})
