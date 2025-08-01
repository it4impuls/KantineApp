
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
from django.http.response import HttpResponse, JsonResponse, Http404
from rest_framework.validators import UniqueForDateValidator
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext as _


class DateValidator(UniqueForDateValidator):
    message = _("The user already ordered today. ")
    def filter_queryset(self, attrs, queryset, field_name, date_field_name):
        return super().filter_queryset(attrs, queryset, field_name, date_field_name)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','userID', 'order_date', 'ordered_item', 'tax']
        validators = [
            DateValidator(
                queryset=Order.objects.all(),
                field='userID', date_field='order_date'
            )
        ]
    order_date = serializers.DateTimeField(read_only=True, default=now)

    
# ViewSets define the view behavior.


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # def create(self, request):
    #     today = localdate(now())
    #     model.validate_unique()
    #     super().create(request)



class UserSerializer(serializers.ModelSerializer):
    def get_last_ordered(self, obj):
        data = OrderSerializer(obj.order_set.latest('order_date')).data
        data.pop("userID")
        return data
    
    
    class Meta:
        model = User
        fields = ['code', "last_ordered"]
    last_ordered = serializers.SerializerMethodField()



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True)
    def ordered_today(self, request, pk=None):
        # if( self.get_object().order_set.filter('order_date__year')):
        #     ...

        obj = self.get_object()
        date_field_name = 'order_date'
        filter_kwargs = {}
        today = now()
        filter_kwargs['%s__day' % date_field_name] = today.day
        filter_kwargs['%s__month' % date_field_name] = today.month
        filter_kwargs['%s__year' % date_field_name] = today.year
        cal =  obj.order_set.all().filter(**filter_kwargs)
        response = HttpResponse()
        if(cal):
            return Response(OrderSerializer(cal.first()).data)
        else:
            return Response({})

    