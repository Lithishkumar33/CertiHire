from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.messages,
        name="messages"
    ),

    path(
        "<int:order_id>/",
        views.chat_room,
        name="chat_room"
    ),
    path(
        "",
        views.messages_list,
        name="messages_list"
    ),

]