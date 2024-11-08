# Generated by Django 5.1.3 on 2024-11-08 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_remove_application_is_accepted_application_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="status",
            field=models.CharField(
                choices=[
                    ("submitted", "Отчет отправлен"),
                    ("accepted", "Отчет принят"),
                    ("rejected", "Отчет отклонен"),
                ],
                default="submitted",
                max_length=20,
            ),
        ),
    ]