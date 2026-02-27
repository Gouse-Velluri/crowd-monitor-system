from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/detection/', include('detection.urls')),
    path('api/alerts/', include('alerts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
