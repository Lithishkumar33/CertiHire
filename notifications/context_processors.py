from .models import Notification

def notification_context(request):

    if request.user.is_authenticated:

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")[:5]

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return {
            "header_notifications": notifications,
            "unread_notifications": unread_count,
        }

    return {
        "header_notifications": [],
        "unread_notifications": 0,
    }