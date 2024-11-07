from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from .forms import ProjectCreationForm
from django.shortcuts import get_object_or_404
from .forms import ApplicationForm
from django.shortcuts import render

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


def home(request):
    return render(request, 'home.html')
