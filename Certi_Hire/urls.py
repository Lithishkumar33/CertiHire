from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", include("landing.urls")),      # Homepage
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("assessment/", include("assessment.urls")),
    path("gigs/", include("gigs.urls")),
    path("orders/", include("orders.urls")),
    path("payments/",include("payments.urls")),
    path("chat/",include("chat.urls")),
    path("notifications/",include("notifications.urls")),
    path("reviews/", include("reviews.urls")),
    path("profile/",include("profiles.urls")),
    path("accounts/",include("django.contrib.auth.urls")),
    path("admin/",include("adminpanel.urls")),

    

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )