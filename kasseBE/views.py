
# Create your views here.
"""
URL configuration for kantineApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from .models import Order, User
from rest_framework import serializers, viewsets
from django.utils.timezone import localdate, now
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'code', 'active', 'enddate']

# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['userID', 'order_date', 'ordered_item', 'tax']
    


    
# ViewSets define the view behavior.


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # def create(self, request):
    #     today = localdate(now())
    #     # serializer = OrderSerializer(data=request.data)
    #     if(self.queryset.filter(userID=request.body.get('UserID'), datetime=today)):
    #         return super().create(request)
    #     else:
    #         return Response
    #     pass

