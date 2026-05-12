import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from .models import Notification


# ======================
# CHAT CONSUMER
# ======================
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]

        self.other_user = await sync_to_async(User.objects.get)(
            id=self.other_user_id
        )

        ids = sorted([self.user.id, self.other_user.id])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)
        message = data["message"]

        # SAVE MESSAGE
        await sync_to_async(Notification.objects.create)(
            sender=self.user,
            reciver=self.other_user,
            content=message
        )

        # 1️⃣ SEND LIVE CHAT MESSAGE
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.username
            }
        )

        # 2️⃣ SEND LIVE INBOX NOTIFICATION
        await self.channel_layer.group_send(
            f"inbox_{self.other_user.id}",
            {
                "type": "inbox_message",
                "sender": self.user.username,
                "message": message
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


# ======================
# INBOX CONSUMER
# ======================
class InboxConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.room_name = f"inbox_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def inbox_message(self, event):
        await self.send(text_data=json.dumps({
            "sender": event["sender"],
            "message": event["message"]
        }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        user = self.scope["user"]

        # 🔴 IMPORTANT: block anonymous users
        if user.is_anonymous:
            await self.close()
            return

        # 🟢 stable group for ALL pages (home, inbox, chat)
        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        print("CONNECTED NOTIFICATION SOCKET:", user.username)


    async def disconnect(self, close_code):

        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )


    async def send_notification(self, event):

        await self.send(text_data=json.dumps({
            "sender": event["sender"],
            "message": event["message"]
        }))
        
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        username = data.get("username", "Anonymous")

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
        }))