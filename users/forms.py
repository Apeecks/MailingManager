from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=50, required=True, help_text="Не обязательное поле."
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username", "password1", "password2")
