from django.contrib import admin
from .models import User, Project, Application, Report

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Application)
admin.site.register(Report)
