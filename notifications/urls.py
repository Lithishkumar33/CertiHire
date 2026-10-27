from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.notification_list,
        name="notifications"
    ),

    path(
        "read/<int:pk>/",
        views.mark_read,
        name="mark_notification_read"
    ),
    path(
        "read-all/",
         views.mark_all_read,
         name="mark_all_notifications",
    ),

]