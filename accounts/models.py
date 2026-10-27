from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # Seller
    is_seller = models.BooleanField(
        default=False
    )
    
    # Assessment
    assessment_passed = models.BooleanField(
        default=False
    )

    malpractice_warnings = models.PositiveIntegerField(
        default=0
    )

    seller_disqualified = models.BooleanField(
        default=False
    )    
    
    assessment_score = models.IntegerField(
        default=0
    )

    assessment_percentage = models.IntegerField(
        default=0
    )
    
    assessment_submitted = models.BooleanField(
        default=False
    )

    assessment_rejected = models.BooleanField(
        default=False
    )

    # Admin approval
    is_approved = models.BooleanField(
        default=False
    )

    # Profile
    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username
    
    
    
