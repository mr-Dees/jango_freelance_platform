from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone


def send_application_accepted_notification(application):
    """Уведомление фрилансеру о принятии заявки"""
    subject = f'Ваша заявка на проект "{application.project.title}" принята'
    message = render_to_string('email/application_accepted.html', {
        'freelancer': application.freelancer,
        'project': application.project,
    })
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [application.freelancer.email],
        html_message=message,
    )


def send_application_rejected_notification(application):
    """Уведомление фрилансеру об отклонении заявки"""
    subject = f'Ваша заявка на проект "{application.project.title}" отклонена'
    message = render_to_string('email/application_rejected.html', {
        'freelancer': application.freelancer,
        'project': application.project,
    })
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [application.freelancer.email],
        html_message=message,
    )


def send_report_accepted_notification(report):
    """Уведомление фрилансеру о принятии отчета"""
    subject = f'Ваш отчет по проекту "{report.project.title}" принят'
    message = render_to_string('email/report_accepted.html', {
        'freelancer': report.freelancer,
        'project': report.project,
    })
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [report.freelancer.email],
        html_message=message,
    )


def send_report_rejected_notification(report):
    """Уведомление фрилансеру об отклонении отчета"""
    subject = f'Ваш отчет по проекту "{report.project.title}" отклонен'
    message = render_to_string('email/report_rejected.html', {
        'freelancer': report.freelancer,
        'project': report.project,
    })
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [report.freelancer.email],
        html_message=message,
    )


def send_new_application_notification(application):
    """Уведомление работодателю о новой заявке"""
    subject = f'Новая заявка на проект "{application.project.title}"'
    message = render_to_string('email/new_application.html', {
        'application': application,
        'project': application.project,
    })
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [application.project.employer.email],
        html_message=message,
    )


def send_new_report_notification(report):
    """Уведомление работодателю о новом отчете"""
    subject = f'Новый отчет по проекту "{report.project.title}"'
    message = render_to_string('email/new_report.html', {
        'report': report,
        'project': report.project,
    })
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [report.project.employer.email],
        html_message=message,
    )


def send_deadline_reminder(application):
    """Уведомление фрилансеру о приближающемся дедлайне"""
    # Вычисляем количество дней до дедлайна
    days_left = (application.project.deadline - timezone.now().date()).days

    subject = f'Напоминание о дедлайне проекта "{application.project.title}"'

    # Формируем текст сообщения с указанием оставшихся дней
    message = render_to_string('email/deadline_reminder.html', {
        'freelancer': application.freelancer,
        'project': application.project,
        'days_left': days_left,  # Передаем количество дней в шаблон
    })

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [application.freelancer.email],
        html_message=message,
    )
