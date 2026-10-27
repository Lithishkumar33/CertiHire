from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.profile,
        name="profile"
    ),
    path(
        "settings/",
        views.settings,
        name="settings"
    ),
    path(
    "change-password/",
    views.change_password,
    name="change_password"
),

]