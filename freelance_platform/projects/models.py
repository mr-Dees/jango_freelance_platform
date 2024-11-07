from django.db import models

# models.py в приложении projects
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('employer', 'Работодатель'),
        ('freelancer', 'Фрилансер'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username


class Project(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'employer'})
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=[('open', 'Открыт'), ('in_progress', 'В работе'), ('completed', 'Завершен')],
        default='open'
    )

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'freelancer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    price_offer = models.DecimalField(max_digits=10, decimal_places=2)
    experience_description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Новое поле статуса

    def __str__(self):
        return f'{self.freelancer.username} - {self.project.title}'


class Report(models.Model):
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to='reports/')
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report for {self.project.title} by {self.freelancer.username}'


class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f'Review for {self.project.title} by {self.reviewer.username}'
