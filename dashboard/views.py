from django.shortcuts import render, get_object_or_404
from locations.models import Location
from alerts.models import Alert


def index(request):
    locations = Location.objects.filter(is_active=True)
    active_alerts = Alert.objects.filter(status=Alert.STATUS_ACTIVE).count()
    context = {
        'locations': locations,
        'active_alerts': active_alerts,
    }
    return render(request, 'dashboard/index.html', context)


def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk, is_active=True)
    logs = location.logs.all()[:100]
    return render(request, 'dashboard/location_detail.html', {
        'location': location,
        'logs': logs,
    })


def alerts_view(request):
    alerts = Alert.objects.select_related('location').order_by('-triggered_at')[:50]
    return render(request, 'dashboard/alerts.html', {'alerts': alerts})
