from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=True,
        label='Rol en el sistema'
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')
