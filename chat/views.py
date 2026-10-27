from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max

from orders.models import Order
from .models import Message


@login_required
def messages(request):

    if request.user.is_seller:

        orders = Order.objects.filter(
            seller=request.user
        ).select_related(
            "buyer",
            "gig"
        )

    else:

        orders = Order.objects.filter(
            buyer=request.user
        ).select_related(
            "seller",
            "gig"
        )

    conversations = []

    for order in orders:

        last_message = Message.objects.filter(
            order=order
        ).order_by("-created_at").first()

        conversations.append({
            "order": order,
            "last_message": last_message
        })

    conversations.sort(
        key=lambda x: x["last_message"].created_at if x["last_message"] else order.created_at,
        reverse=True
    )

    return render(
        request,
        "chat/messages.html",
        {
            "conversations": conversations
        }
    )


@login_required
def chat_room(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.user != order.buyer and request.user != order.seller:
        return redirect("dashboard")

    messages = Message.objects.filter(
        order=order
    ).order_by("created_at")

    Message.objects.filter(
        order=order
    ).exclude(
        sender=request.user
    ).update(
        is_read=True
    )

    return render(
        request,
        "chat/chat_room.html",
        {
            "order": order,
            "messages": messages,
        }
    )




@login_required
def messages_list(request):

    messages = (
        Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        )
        .select_related(
            "sender",
            "receiver"
        )
        .order_by("-timestamp")
    )

    conversations = {}
    conversation_list = []

    for msg in messages:

        other_user = (
            msg.receiver
            if msg.sender == request.user
            else msg.sender
        )

        if other_user.id not in conversations:

            conversations[other_user.id] = True

            conversation_list.append({

                "user": other_user,

                "last_message": msg.message,

                "timestamp": msg.timestamp,

                "unread": Message.objects.filter(
                    sender=other_user,
                    receiver=request.user,
                    is_read=False
                ).count()

            })

    return render(
        request,
        "chat/messages.html",
        {
            "conversations": conversation_list
        }
    )