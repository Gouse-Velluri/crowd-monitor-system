import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from locations.models import Location
from locations.serializers import LocationSerializer


class CrowdConsumer(AsyncWebsocketConsumer):
    """Consumer that receives updates for ALL locations."""

    GROUP_NAME = 'crowd_all'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()
        # Send current state on connect
        locations = await self._get_all_locations()
        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'data': locations,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        """Handle ping from client."""
        data = json.loads(text_data)
        if data.get('type') == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))

    async def crowd_update(self, event):
        """Relay crowd update to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'crowd_update',
            'data': event['data'],
        }))

    @database_sync_to_async
    def _get_all_locations(self):
        qs = Location.objects.filter(is_active=True)
        return LocationSerializer(qs, many=True).data


class LocationCrowdConsumer(AsyncWebsocketConsumer):
    """Consumer for a SINGLE location's updates."""

    async def connect(self):
        self.location_id = self.scope['url_route']['kwargs']['location_id']
        self.group_name = f'crowd_{self.location_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def crowd_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'crowd_update',
            'data': event['data'],
        }))
