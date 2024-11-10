from django.db import models
from django.utils import timezone
from datetime import timedelta
import threading
import time
from .models import Application
from .notifications import send_deadline_reminder


class DeadlineChecker(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.daemon = True
        self._last_check = None

    def run(self):
        # Настраиваем в какой час будет проверка дедлайнов
        current_time = timezone.now()
        checked_hour = 14

        # Если при запуске сервера не проверяемый час, вручную запускаем проверку дедлайнов
        if current_time.hour != checked_hour:
            self.check_deadlines()

        while not self._stop_event.is_set():
            try:
                current_time = timezone.now()

                # Проверяем раз в день в заявленный час
                if (current_time.hour == checked_hour and
                        (self._last_check is None or
                         current_time.date() > self._last_check.date())):
                    self.check_deadlines()

                time.sleep(60*10)

            except Exception as e:
                print(f"Ошибка при проверке дедлайнов: {e}")
                time.sleep(60)

    def check_deadlines(self):
        current_time = timezone.now()
        # print(f"Начинаем проверку дедлайнов: {current_time}")

        deadline_threshold = current_time.date() + timedelta(days=2)

        # Получаем заявки, где не отправлено уведомление или отправлено в другой день
        active_applications = Application.objects.filter(
            status='accepted',
            project__deadline__lte=deadline_threshold,
            project__deadline__gt=current_time.date()
        ).filter(
            models.Q(deadline_notification_sent__isnull=True) |  # Уведомление еще не отправлялось
            models.Q(deadline_notification_sent__lt=current_time.date())  # Или отправлялось в предыдущие дни
        )

        print(f"Найдено активных заявок с приближающимся дедлайном: {active_applications.count()}")

        for application in active_applications:
            days_left = (application.project.deadline - current_time.date()).days
            # print(f"Проект: '{application.project.title}', осталось дней: {days_left}")

            send_deadline_reminder(application)
            print(f'Отправлено напоминание для проекта {application.project.title} (осталось {days_left} дней)')

            # Обновляем дату отправки уведомления
            application.deadline_notification_sent = current_time.date()
            application.save()

    def stop(self):
        self._stop_event.set()
