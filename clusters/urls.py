from django.urls import path
from .views import (
    ClusterListCreateView,
    NamespaceListCreateView, NamespaceDetailView,
    AppListCreateView, AppDetailView
)

urlpatterns = [
    path('cluster', ClusterListCreateView.as_view(), name='cluster-list-create'),
    path('namespace', NamespaceListCreateView.as_view(), name='namespace-list-create'),
    path('namespace/<int:pk>', NamespaceDetailView.as_view(), name='namespace-detail'),
    path('app', AppListCreateView.as_view(), name='app-list-create'),
    path('app/<int:pk>', AppDetailView.as_view(), name='app-detail'),
]