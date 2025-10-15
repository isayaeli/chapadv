from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]