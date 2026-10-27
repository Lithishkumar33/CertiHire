from .models import Message
from orders.models import Order


def message_context(request):

    if not request.user.is_authenticated:
        return {
            "header_messages": [],
            "unread_messages": 0,
        }

    if request.user.is_seller:

        orders = Order.objects.filter(
            seller=request.user
        )

    else:

        orders = Order.objects.filter(
            buyer=request.user
        )

    messages = Message.objects.filter(
        order__in=orders
    ).select_related(
        "sender",
        "order",
        "order__gig"
    ).order_by("-created_at")[:5]

    unread = Message.objects.filter(
        order__in=orders,
        is_read=False
    ).exclude(
        sender=request.user
    ).count()

    return {

        "header_messages": messages,

        "unread_messages": unread,

    }