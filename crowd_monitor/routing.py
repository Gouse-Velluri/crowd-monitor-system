from django.urls import re_path
from locations import consumers

websocket_urlpatterns = [
    re_path(r'ws/crowd/$', consumers.CrowdConsumer.as_asgi()),
    re_path(r'ws/crowd/(?P<location_id>\d+)/$', consumers.LocationCrowdConsumer.as_asgi()),
]
