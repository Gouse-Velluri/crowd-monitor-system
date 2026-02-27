from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'location', 'location_name', 'alert_type', 'message',
            'triggered_at', 'resolved_at', 'status',
            'people_count_at_trigger', 'occupancy_at_trigger',
        ]


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlertSerializer

    def get_queryset(self):
        qs = Alert.objects.select_related('location')
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())
        location = self.request.query_params.get('location')
        if location:
            qs = qs.filter(location_id=location)
        return qs

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        if alert.status == Alert.STATUS_RESOLVED:
            return Response({'detail': 'Already resolved.'})
        alert.resolve()
        return Response(AlertSerializer(alert).data)
