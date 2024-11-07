from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.shortcuts import get_object_or_404
from .forms import ApplicationForm
from .forms import ProjectCreationForm
from django.contrib.auth.decorators import login_required
from .models import Application

from .models import Project


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


# Личный кабинет фрилансера
def freelancer_dashboard(request):
    return render(request, 'freelancer_dashboard.html')


# Личный кабинет работодателя
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')


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

    available_projects = Project.objects.filter(status='open').exclude(application__freelancer=request.user)

    return render(request, 'freelancer_dashboard.html', {'available_projects': available_projects})


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
