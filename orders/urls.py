from django.urls import path
from . import views

urlpatterns = [

    path(
        "summary/<int:gig_id>/",
        views.order_summary,
        name="order_summary"
    ),
    path(
    "accept/<int:pk>/",
    views.accept_order,
    name="accept_order"
    ),
    path(
    "start/<int:pk>/",
    views.start_order,
    name="start_order"
    ),
    path(
    "",
    views.orders,
    name="orders"
    ),
    path(
    "<int:pk>/",
    views.order_detail,
    name="order_detail"
    ),
    path(
    "deliver/<int:pk>/",
    views.upload_deliverable,
    name="upload_deliverable"
    ),
    path(
    "approve/<int:pk>/",
    views.approve_delivery,
    name="approve_delivery"
    ),
    path(
    "revision/<int:pk>/",
    views.request_revision,
    name="request_revision"
    ),
     path(
        "certificate/<int:pk>/",
        views.download_certificate,
        name="download_certificate"
    ),
]
