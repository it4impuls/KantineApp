
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
from django.utils.timezone import now
from io import BytesIO
from barcode import Code128
from barcode.writer import SVGWriter
from django.http.response import HttpResponse,  FileResponse
from rest_framework.validators import UniqueForDateValidator, qs_exists, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404

@action(detail=True, methods=["GET"])
def get_barcode(pk=None) -> BytesIO:
    
    # if(not obj):
    #     raise
    rv = BytesIO()
    Code128("0"*(Code128.digits-len(pk))+pk, writer=SVGWriter()).write(rv)
    return rv
    

def ordered_today(self, pk):
    # if( self.get_object().order_set.filter('order_date__year')):
    #     ...

    obj = get_object_or_404(User, code=pk)
    date_field_name = 'order_date'
    filter_kwargs = {}
    today = now()
    filter_kwargs['%s__day' % date_field_name] = today.day
    filter_kwargs['%s__month' % date_field_name] = today.month
    filter_kwargs['%s__year' % date_field_name] = today.year
    cal =  obj.order_set.all().filter(**filter_kwargs)
    if(cal):
        OrderSerializer(cal.first()).data
    else:
        return {}

class DateValidator(UniqueForDateValidator):
    message = _("The user already ordered today. ")
    message = "Der Kunde hat heute bereits bestellt."
    def filter_queryset(self, attrs, queryset, field_name, date_field_name):
        ret = super().filter_queryset(attrs, queryset, field_name, date_field_name)
        # if(ret):
        #     self.message = _(str(self.message.format(order=OrderHyperlinkSerializer(ret[0]).data)))
        return ret

    def __call__(self, attrs, serializer):
        # Determine the underlying model field names. These may not be the
        # same as the serializer field names if `source=<>` is set.
        field_name = serializer.fields[self.field].source_attrs[-1]
        date_field_name = serializer.fields[self.date_field].source_attrs[-1]

        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset, field_name, date_field_name)
        queryset = self.exclude_current_instance(attrs, queryset, serializer.instance)
        if qs_exists(queryset):
            message = self.message.format(date_field=self.date_field)
            raise ValidationError({
                self.field: message,
                "order":  OrderHyperlinkSerializer(queryset.first(), context={'request': None}).data
            }, code='unique')

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

serializers.HyperlinkedModelSerializer()
    
# ViewSets define the view behavior.


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # def create(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #     except Exception as e:
    #         response = self.handle_exception(e)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class UserSerializer(serializers.ModelSerializer):
    def get_last_ordered(self, obj):
        if(obj.order_set.all()):
            data = OrderSerializer(obj.order_set.latest('order_date')).data
            data.pop("userID")
            return data
        else: return None
    
    
    class Meta:
        model = User
        fields = fields = ['firstname', 'lastname', 'code', 'active', 'last_ordered']
    last_ordered = serializers.SerializerMethodField()
    firstname = serializers.CharField(write_only=True)
    lastname = serializers.CharField(write_only=True)
    # enddate = serializers.DateTimeField(write_only=True)

   


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=["GET"])
    def barcode(self,request, pk=None):
        try:    # make sure user actually exists
            get_object_or_404(User, code=pk)
        except Exception as e:
            return self.handle_exception(e)
        rv = get_barcode(pk)
        rv.seek(0)
        return FileResponse(rv, filename=pk+".svg", as_attachment=False)

    @action(detail=True)
    def ordered_today(self, request, pk=None):
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

class OrderHyperlinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ['url','userID', 'order_date', 'ordered_item', 'tax']
        validators = [
            DateValidator(
                queryset=Order.objects.all(),
                field='userID', date_field='order_date'
            )
        ]
    order_date = serializers.DateTimeField(read_only=True, default=now)