from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):

    is_seller = forms.BooleanField(
        required=False,
        label="Register as Seller"
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "is_seller",
            "password1",
            "password2",
        ]