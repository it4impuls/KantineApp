from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, serializers, viewsets

router = routers.DefaultRouter()

urlpatterns = [
    path('', include('kasseBE.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls', namespace='rest_framework'))
]