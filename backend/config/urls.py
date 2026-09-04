from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clusters.urls')),
    path('backup/', include('backup.urls')),
    path('api/', include('backup.urls')),
]