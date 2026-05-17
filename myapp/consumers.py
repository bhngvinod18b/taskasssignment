import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]

        # import models here to avoid AppRegistryNotReady
        from django.contrib.auth.models import User
        from .models import Notification

        self.other_user = await sync_to_async(User.objects.get)(id=self.other_user_id)

        ids = sorted([self.user.id, self.other_user.id])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        from .models import Notification
        await sync_to_async(Notification.objects.create)(
            sender=self.user,
            reciver=self.other_user,
            content=message
        )

        await self.channel_layer.group_send(
            self.room_name,
            {"type": "chat_message", "message": message, "sender": self.user.username}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.room_name = f"inbox_{self.user.id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def inbox_message(self, event):
        await self.send(text_data=json.dumps(event))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        # import models here if needed
        # from .models import Notification

        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event))