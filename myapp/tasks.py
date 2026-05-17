from celery import shared_task
from django.contrib.auth.models import User
from .models import Notification

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def create_task_notification(user_id, manager_id, task_text):

    user = User.objects.get(id=user_id)
    manager = User.objects.get(id=manager_id)

    # 1. Save in DB
    notification = Notification.objects.create(
        sender=manager,
        reciver=user,
        content=f"📌 New Task Assigned: {task_text}"
    )

    print("🔥 CELERY TASK EXECUTED")

    # 2. SEND REAL-TIME WEBSOCKET NOTIFICATION
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",   # MUST MATCH consumer group
        {
            "type": "send_notification",
            "sender": manager.username,
            "message": f"📌 New Task Assigned: {task_text}",
        }
    )

    return "Notification created + sent"