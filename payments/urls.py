from django.urls import path
from . import views

urlpatterns = [

    path(
        "pay/<int:gig_id>/",
        views.initiate_payment,
        name="initiate_payment"
    ),

    path(
        "success/<str:order_id>/",
        views.payment_success,
        name="payment_success"
    ),

    path(
        "failed/",
        views.payment_failed,
        name="payment_failed"
    ),
    path(
        "webhook/",
        views.cashfree_webhook,
        name="cashfree_webhook"
    ),
    path(
        "history/",
        views.payment_history,
        name="payment_history"
    ),
    path(
        "invoice/<int:payment_id>/",
        views.download_invoice,
        name="download_invoice",
    ),
]