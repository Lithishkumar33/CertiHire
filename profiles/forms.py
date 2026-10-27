from django import forms
from .models import Profile
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError


class ProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = [
            "profile_photo",
            "phone",
            "bio",
            "skills",
            "location",
            "website",
            "github",
            "linkedin",
        ]

        widgets = {

            "bio": forms.Textarea(
                attrs={
                    "rows":4
                }
            )

        }
        
class SettingsForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = [
            "dark_mode",

            "email_notifications",
            "push_notifications",

            "order_notifications",
            "message_notifications",
            "review_notifications",
            "payment_notifications",
            "promotional_notifications",

            "public_profile",
            "show_phone",
            "show_email",
            "show_online",
        ]

        widgets = {

            "dark_mode": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "email_notifications": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "push_notifications": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "order_notifications": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "message_notifications": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "review_notifications": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "payment_notifications": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "promotional_notifications": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "public_profile": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "show_phone": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "show_email": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),

            "show_online": forms.CheckboxInput(
                attrs={"class": "settings-toggle"}
            ),
        }
        



class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your current password",
                "autocomplete": "current-password"
            }
        )
    )

    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your new password",
                "autocomplete": "new-password"
            }
        )
    )

    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Re-enter your new password",
                "autocomplete": "new-password"
            }
        )
    )

    def __init__(self, user, *args, **kwargs):

        self.user = user

        super().__init__(*args, **kwargs)

    def clean_current_password(self):

        password = self.cleaned_data.get("current_password")

        if not self.user.check_password(password):

            raise forms.ValidationError(
                "Current password is incorrect."
            )

        return password

    def clean_new_password(self):

        password = self.cleaned_data.get("new_password")

        password_validation.validate_password(
            password,
            self.user
        )

        return password

    def clean(self):

        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if (
            new_password
            and confirm_password
            and new_password != confirm_password
        ):

            raise forms.ValidationError(
                "New password and confirmation password do not match."
            )

        return cleaned_data