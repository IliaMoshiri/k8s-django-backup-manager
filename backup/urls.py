from django.urls import path
from .views import BackupAPIView

urlpatterns = [
    path('', BackupAPIView.as_view(), name='backup_root'),
    path('<str:backup_id>/', BackupAPIView.as_view(), name='backup_detail'),
]