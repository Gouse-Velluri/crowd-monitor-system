from django.contrib import admin
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['location', 'alert_type', 'status', 'people_count_at_trigger', 'triggered_at', 'resolved_at']
    list_filter = ['status', 'alert_type']
    actions = ['resolve_selected']

    def resolve_selected(self, request, queryset):
        for alert in queryset.filter(status=Alert.STATUS_ACTIVE):
            alert.resolve()
        self.message_user(request, "Selected alerts resolved.")
    resolve_selected.short_description = "Resolve selected alerts"
