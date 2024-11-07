from django.urls import path
from .views import home, freelancer_dashboard, employer_dashboard, register, redirect_after_login, apply_for_project, \
    upload_report, view_applications, cancel_application, application_detail, cancel_project, project_detail, \
    retry_application, delete_application
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),  # Стартовая страница
    path('freelancer/', freelancer_dashboard, name='freelancer_dashboard'),  # Личный кабинет фрилансера
    path('employer/', employer_dashboard, name='employer_dashboard'),  # Личный кабинет работодателя
    path('register/', register, name='register'),  # Регистрация
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Вход
    path('redirect/', redirect_after_login, name='redirect_after_login'),  # Кастомное перенаправление
    # Подача и отмена заявок (для фрилансеров)
    path('apply/<int:project_id>/', apply_for_project, name='apply_for_project'),
    path('cancel_application/<int:project_id>/', cancel_application, name='cancel_application'),
    # Просмотр заявок (для работодателей)
    path('employer/project/<int:project_id>/applications/', view_applications, name='view_applications'),
    # Просмотр деталей конкретной заявки (для работодателей)
    path('employer/application/<int:application_id>/', application_detail, name='application_detail'),
    # Отмена (удаление) проекта (для работодателей)
    path('employer/project/<int:project_id>/cancel/', cancel_project, name='cancel_project'),
    # Просмотр деталей проекта (для работодателей)
    path('employer/project/<int:project_id>/', project_detail, name='project_detail'),
    # Повторная подача и удаление заявок (для фрилансеров)
    path('retry_application/<int:application_id>/', retry_application, name='retry_application'),
    path('delete_application/<int:application_id>/', delete_application, name='delete_application'),
]
