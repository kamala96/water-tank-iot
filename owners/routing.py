from . import consumers
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/account/(?P<owner_topic>\w+)/$", consumers.TankOwnerConsumer.as_asgi()),
]
