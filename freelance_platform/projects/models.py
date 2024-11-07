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

    def __str__(self):
        return self.title


class Application(models.Model):
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'freelancer'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    price_offer = models.DecimalField(max_digits=10, decimal_places=2)
    experience_description = models.TextField()
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.freelancer.username} - {self.project.title}'


class Report(models.Model):
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to='reports/')
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report for {self.project.title} by {self.freelancer.username}'
