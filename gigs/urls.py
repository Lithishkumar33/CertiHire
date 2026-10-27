from django.urls import path
from . import views

urlpatterns = [

    path(
        "create/",
        views.create_gig,
        name="create_gig",
    ),

    path(
        "my-gigs/",
        views.my_gigs,
        name="my_gigs",
    ),
    path(
        "",
        views.gig_list,
        name="gig_list",
    ),
    path(
    "<int:pk>/",
    views.gig_detail,
    name="gig_detail"
    ),
    path(
    "edit/<int:pk>/",
    views.edit_gig,
    name="edit_gig"
    ),
    path(
    "delete/<int:pk>/",
    views.delete_gig,
    name="delete_gig"
    ),
]