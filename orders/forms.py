from django import forms
from .models import Deliverable


class DeliverableForm(forms.ModelForm):

    class Meta:

        model = Deliverable

        fields = [

            "file",

            "message"

        ]

        widgets = {

            "file": forms.FileInput(

                attrs={

                    "class":"form-control"

                }

            ),

            "message": forms.Textarea(

                attrs={

                    "class":"form-control",

                    "rows":4,

                    "placeholder":"Write a delivery note..."

                }

            )

        }