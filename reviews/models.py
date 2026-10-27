from django.db import models
from django.conf import settings

from orders.models import Order


class Review(models.Model):

    RATING_CHOICES = [

        (1, "1 Star"),

        (2, "2 Stars"),

        (3, "3 Stars"),

        (4, "4 Stars"),

        (5, "5 Stars"),

    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="review"
    )

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    title = models.CharField(
        max_length=100
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

    def __str__(self):

        return f"{self.buyer.username} → {self.seller.username} ({self.rating})"