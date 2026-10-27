from django.urls import path
from . import views
from .views import (
    register_view,
    login_view,
    logout_view
)

urlpatterns = [

    path(
        "register/",
        register_view,
        name="register"
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),
    path(
        "assessment-required/",
        views.assessment_required,
        name="assessment_required"
    ),
    path(
        "assessment-required/",
        views.assessment_required,
        name="assessment_required"
    ),

    path(
        "assessment-pending/",
        views.assessment_pending,
        name="assessment_pending"
    ),
    path(
    "forgot-password/",
    views.forgot_password,
    name="forgot_password"
),

path(
    "verify-reset-otp/",
    views.verify_reset_otp,
    name="verify_reset_otp"
),

path(
    "reset-password/",
    views.reset_password,
    name="reset_password"
),
path(
    "password_change/",
    views.password_change,
    name="password_change"
),
]