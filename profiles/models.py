from django.db import models
from django.conf import settings


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # =====================================================
    # PROFILE INFORMATION
    # =====================================================

    profile_photo = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    skills = models.CharField(
        max_length=300,
        blank=True,
        help_text="Example: Python, Django, React"
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    github = models.URLField(
        blank=True
    )

    linkedin = models.URLField(
        blank=True
    )


    # =====================================================
    # APPEARANCE
    # =====================================================

    dark_mode = models.BooleanField(
        default=False
    )


    # =====================================================
    # GENERAL NOTIFICATIONS
    # =====================================================

    email_notifications = models.BooleanField(
        default=True
    )

    push_notifications = models.BooleanField(
        default=True
    )


    # =====================================================
    # ORDER & ACTIVITY NOTIFICATIONS
    # =====================================================

    order_notifications = models.BooleanField(
        default=True
    )

    message_notifications = models.BooleanField(
        default=True
    )

    review_notifications = models.BooleanField(
        default=True
    )

    payment_notifications = models.BooleanField(
        default=True
    )

    promotional_notifications = models.BooleanField(
        default=False
    )


    # =====================================================
    # PRIVACY
    # =====================================================

    public_profile = models.BooleanField(
        default=True
    )

    show_phone = models.BooleanField(
        default=False
    )

    show_email = models.BooleanField(
        default=False
    )

    show_online = models.BooleanField(
        default=True
    )


    # =====================================================
    # CREATED
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.user.username