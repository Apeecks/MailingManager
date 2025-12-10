from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=50, required=True, help_text="Не обязательное поле."
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username", "phone_number", "avatar", "country", "password1", "password2")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "phone_number", "avatar", "country"]
