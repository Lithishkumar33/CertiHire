import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from orders.models import Order
from .models import Message
from notifications.utils import create_notification

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.room_group_name = f"chat_{self.order_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        # -----------------------------
        # Typing Indicator
        # -----------------------------
        if data.get("event") == "typing":

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_indicator",
                    "username": data["username"],
                }
            )

            return

        # -----------------------------
        # Normal Chat Message
        # -----------------------------
        sender_id = data["sender_id"]
        message = data["message"].strip()

        if not message:
            return

        sender = await sync_to_async(User.objects.get)(id=sender_id)

        order = await sync_to_async(
            Order.objects.select_related(
                "buyer",
                "seller",
                "gig"
            ).get
        )(id=self.order_id)

        # Save message
        await sync_to_async(Message.objects.create)(
            order=order,
            sender=sender,
            message=message
        )

        # Receiver
        receiver = (
            order.seller
            if sender.id == order.buyer.id
            else order.buyer
        )

        # Notification
        await sync_to_async(create_notification)(
            user=receiver,
            title="New Message",
            message=f"{sender.username}: {message[:60]}",
            link=f"/chat/{order.id}/"
        )

        # Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.username,
                "sender_id": sender.id,
            }
        )

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps({
                "event": "message",
                "message": event["message"],
                "sender": event["sender"],
                "sender_id": event["sender_id"],
            })
        )

    async def typing_indicator(self, event):

        await self.send(
            text_data=json.dumps({
                "event": "typing",
                "username": event["username"],
            })
        )