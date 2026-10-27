from django import forms
from .models import Gig


class GigForm(forms.ModelForm):

    class Meta:
        model = Gig
        fields = [
            "title",
            "description",
            "category",
            "price",
            "delivery_days",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "delivery_days": forms.NumberInput(attrs={"class": "form-control"}),
        }

