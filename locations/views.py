from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Location, CrowdLog
from .serializers import LocationSerializer, LocationUpdateSerializer, CrowdLogSerializer
from alerts.utils import check_and_trigger_alerts


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer

    @action(detail=True, methods=['post'], url_path='update-count')
    def update_count(self, request, pk=None):
        location = self.get_object()
        ser = LocationUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        count = ser.validated_data['count']
        source = ser.validated_data['source']

        location.update_count(count)

        # Save log
        log = CrowdLog.objects.create(
            location=location,
            people_count=count,
            density_level=location.density_level,
            occupancy_percentage=location.occupancy_percentage,
            source=source,
        )

        # Check alerts
        check_and_trigger_alerts(location)

        # Broadcast via WebSocket
        _broadcast_update(location)

        return Response(LocationSerializer(location).data)

    @action(detail=True, methods=['get'], url_path='logs')
    def logs(self, request, pk=None):
        location = self.get_object()
        limit = int(request.query_params.get('limit', 50))
        logs = location.logs.all()[:limit]
        return Response(CrowdLogSerializer(logs, many=True).data)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        location = self.get_object()
        from django.db.models import Avg, Max, Min
        from datetime import timedelta

        now = timezone.now()
        last_24h = location.logs.filter(timestamp__gte=now - timedelta(hours=24))
        agg = last_24h.aggregate(
            avg_count=Avg('people_count'),
            max_count=Max('people_count'),
            min_count=Min('people_count'),
        )
        return Response({
            'location': LocationSerializer(location).data,
            'last_24h': {
                **agg,
                'total_readings': last_24h.count(),
            }
        })


class CrowdLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CrowdLogSerializer

    def get_queryset(self):
        qs = CrowdLog.objects.select_related('location')
        location_id = self.request.query_params.get('location')
        if location_id:
            qs = qs.filter(location_id=location_id)
        return qs[:100]


def _broadcast_update(location: Location):
    channel_layer = get_channel_layer()
    payload = {
        'type': 'crowd_update',
        'data': {
            'location_id': location.id,
            'location_name': location.name,
            'current_count': location.current_count,
            'capacity_limit': location.capacity_limit,
            'density_level': location.density_level,
            'occupancy_percentage': location.occupancy_percentage,
            'last_updated': location.last_updated.isoformat(),
        }
    }
    # Broadcast to all-locations group
    async_to_sync(channel_layer.group_send)('crowd_all', payload)
    # Broadcast to location-specific group
    async_to_sync(channel_layer.group_send)(f'crowd_{location.id}', payload)
