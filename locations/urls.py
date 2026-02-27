from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, CrowdLogViewSet

router = DefaultRouter()
router.register(r'', LocationViewSet, basename='location')
router.register(r'logs/all', CrowdLogViewSet, basename='crowdlog')

urlpatterns = [
    path('', include(router.urls)),
]
