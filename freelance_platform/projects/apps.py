from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projects"

    def ready(self):
        # Импортируем здесь, чтобы избежать циклических импортов
        from .tasks import DeadlineChecker

        # Запускаем проверку дедлайнов в отдельном потоке
        checker = DeadlineChecker()
        checker.start()
