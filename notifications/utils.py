from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def create_notification(
    user,
    title,
    message,
    link=""
):

    # Save notification
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link
    )

    # Send live update
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "notify",
            "title": title,
            "message": message,
            "link": link,
            "notification_id": notification.id,
        }
    )

    return notification