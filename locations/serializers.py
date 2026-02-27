from rest_framework import serializers
from .models import Location, CrowdLog


class LocationSerializer(serializers.ModelSerializer):
    occupancy_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'description', 'latitude', 'longitude',
            'capacity_limit', 'current_count', 'density_level',
            'occupancy_percentage', 'is_active', 'camera_url', 'last_updated',
        ]
        read_only_fields = ['current_count', 'density_level', 'last_updated']


class LocationUpdateSerializer(serializers.Serializer):
    count = serializers.IntegerField(min_value=0)
    source = serializers.ChoiceField(choices=['AI', 'MANUAL'], default='MANUAL')


class CrowdLogSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = CrowdLog
        fields = [
            'id', 'location', 'location_name', 'people_count',
            'density_level', 'occupancy_percentage', 'source', 'timestamp',
        ]
