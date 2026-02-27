from django.urls import path
from .views import DetectFromImageView, DetectAndUpdateView

urlpatterns = [
    path('detect/', DetectFromImageView.as_view(), name='detect-image'),
    path('detect/<int:location_id>/', DetectAndUpdateView.as_view(), name='detect-update'),
]
