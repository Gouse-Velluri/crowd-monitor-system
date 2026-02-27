from django.contrib import admin
from .models import Location, CrowdLog


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_count', 'capacity_limit', 'density_level', 'occupancy_percentage', 'last_updated']
    list_filter = ['density_level', 'is_active']
    search_fields = ['name']
    readonly_fields = ['current_count', 'density_level', 'last_updated']


@admin.register(CrowdLog)
class CrowdLogAdmin(admin.ModelAdmin):
    list_display = ['location', 'people_count', 'density_level', 'occupancy_percentage', 'source', 'timestamp']
    list_filter = ['density_level', 'source', 'location']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
