from django.db import models
from django.conf import settings


class Gig(models.Model):

    CATEGORY_CHOICES = [
        ("Graphics & Design", "Graphics & Design"),
        ("Digital Marketing", "Digital Marketing"),
        ("Writing & Translation", "Writing & Translation"),
        ("Video & Animation", "Video & Animation"),
        ("Music", "Music"),
        ("Programming & Tech", "Programming & Tech"),
        ("Business", "Business"),
        ("Lifestyle", "Lifestyle"),
        ("Data", "Data"),
        ("Photography", "Photography"),
    ]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gigs"
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    delivery_days = models.PositiveIntegerField()

    image = models.ImageField(
        upload_to="gig_images/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title