from django.urls import re_path

def get_websocket_urlpatterns():
    from . import consumers
    return [
        re_path(r'ws/chat/(?P<user_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
        re_path(r'ws/inbox/$', consumers.InboxConsumer.as_asgi()),
        re_path(r'ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    ]

websocket_urlpatterns = get_websocket_urlpatterns()