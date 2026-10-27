from django.db import models
from django.conf import settings
from gigs.models import Gig


class Order(models.Model):

    STATUS_CHOICES = [

    ("Pending", "Pending"),

    ("Confirmed", "Confirmed"),

    ("In Progress", "In Progress"),

    ("Delivered", "Delivered"),

    ("Revision", "Revision"),

    ("Completed", "Completed"),

    ("Cancelled", "Cancelled"),

]

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="buyer_orders"
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_orders"
    )

    gig = models.ForeignKey(
        Gig,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    certificate_downloaded = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Order #{self.id}"

class Deliverable(models.Model):

    order = models.ForeignKey(

        Order,

        on_delete=models.CASCADE,

        related_name="deliverables"

    )

    uploaded_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE

    )

    file = models.FileField(

        upload_to="deliverables/"

    )

    message = models.TextField(

        blank=True

    )

    uploaded_at = models.DateTimeField(

        auto_now_add=True

    )

    def __str__(self):

        return self.file.name