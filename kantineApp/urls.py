from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
router = routers.DefaultRouter()

urlpatterns = [
    path('', include('kasseBE.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns += staticfiles_urlpatterns()