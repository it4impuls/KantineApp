from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import is_loggedin, login

urlpatterns = [
    path('', include('kasseBE.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls', namespace='rest_framework')),
    path('auth/login/', login, name='login'),
    path('auth/verify/', is_loggedin, name='logged_in')
]

urlpatterns += staticfiles_urlpatterns()
