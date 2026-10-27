from django.db import models
from django.conf import settings

from gigs.models import Gig
from orders.models import Order


class Payment(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("SUCCESS", "Success"),

        ("FAILED", "Failed"),

    ]

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    gig = models.ForeignKey(
        Gig,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payment"
    )

    cashfree_order_id = models.CharField(
        max_length=150,
        unique=True
    )

    payment_session_id = models.CharField(
        max_length=255,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

    def __str__(self):

        return self.cashfree_order_id