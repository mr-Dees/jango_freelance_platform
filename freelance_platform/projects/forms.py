# forms.py в приложении projects
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Project
from .models import Application


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']


# forms.py в приложении projects
class ProjectCreationForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'budget', 'deadline']


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['price_offer', 'experience_description']
