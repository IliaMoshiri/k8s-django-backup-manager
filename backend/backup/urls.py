from django.urls import path
from .views import (
    BackupAPIView,
    ClusterAPIView,
    NamespaceAPIView,
    AppAPIView
)

urlpatterns = [
    path('backup/', BackupAPIView.as_view(), name='backup_root'),
    path('backup/<str:backup_id>/', BackupAPIView.as_view(), name='backup_detail'),

    path('cluster/', ClusterAPIView.as_view(), name='cluster_list'),
    
    path('namespace/', NamespaceAPIView.as_view(), name='namespace_list'),
    path('namespace/<int:pk>/', NamespaceAPIView.as_view(), name='namespace_detail'),
    
    path('app/', AppAPIView.as_view(), name='app_list'),
]