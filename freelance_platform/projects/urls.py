from django.urls import path
from .views import home, freelancer_dashboard, employer_dashboard, register, redirect_after_login, apply_for_project, \
    upload_report
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),  # Стартовая страница
    path('freelancer/', freelancer_dashboard, name='freelancer_dashboard'),  # Личный кабинет фрилансера
    path('employer/', employer_dashboard, name='employer_dashboard'),  # Личный кабинет работодателя
    path('register/', register, name='register'),  # Регистрация
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Вход
    path('redirect/', redirect_after_login, name='redirect_after_login'),  # Кастомное перенаправление
    # Подача заявки на проект (для фрилансеров)
    path('apply/<int:project_id>/', apply_for_project, name='apply_for_project'),
    # Загрузка отчета по проекту (для фрилансеров)
    path('upload_report/<int:project_id>/', upload_report, name='upload_report'),
]
