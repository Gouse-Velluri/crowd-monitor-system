import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import crowd_monitor.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowd_monitor.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            crowd_monitor.routing.websocket_urlpatterns
        )
    ),
})
