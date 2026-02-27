from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('location/<int:pk>/', views.location_detail, name='location-detail'),
    path('alerts/', views.alerts_view, name='alerts'),
]
