import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collab_expense_tracker.settings')

# Now import Django components
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from tracker import routing  # Only routing, not models or views

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
