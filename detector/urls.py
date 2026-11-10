from django.urls import path
from . import views
from .api_views import PredictAPIView

urlpatterns = [
    path('', views.upload_image, name='home'),
    path('history/', views.history, name='history'),
    path('history/<int:pk>/', views.scan_detail, name='scan_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('history/<int:pk>/download/', views.download_report, name='download_report'),
    path('history/<int:pk>/delete/', views.delete_scan, name='delete_scan'),
    path('api/predict/', PredictAPIView.as_view(), name='api_predict'), 
    path('add-crop/', views.add_crop_cycle, name='add_crop_cycle'),
]