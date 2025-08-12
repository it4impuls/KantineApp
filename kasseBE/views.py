
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

from .models import Order, User, OrderBill
from rest_framework import serializers, viewsets
from django.utils.timezone import now
from io import BytesIO
from barcode import Code128
from barcode.writer import SVGWriter
from django.http.response import HttpResponse,  FileResponse
from rest_framework.validators import UniqueForDateValidator, qs_exists, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404, render
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import FileExtensionValidator
from django import forms
from csv import DictReader


class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'accept': 'text/csv'}),
                           validators=[FileExtensionValidator(["csv"], _("nur csv-Dateien sind erlaubt"))])


def get_barcode(pk) -> BytesIO:
    writer = SVGWriter()
    options = {"module_width": 0.2, "module_height": 3,
               "text_distance": 2, "font_size": 6}
    rv = BytesIO()
    Code128("0"*(Code128.digits-len(pk))+pk,
            writer=writer).write(rv, options=options)
    return rv


def add_users_from_file(f: InMemoryUploadedFile):
    file = f.read().decode('utf-8').split("\n")
    ret = {"added": [], "duplicate": []}
    try:
        for line in DictReader(file, delimiter=",", fieldnames=["firstname", "lastname"]):
            existing = User.objects.all().filter(**line)
            if (existing):
                ret['duplicate'].append(line)
                continue
            u = User(**line)
            line["code"] = u.code
            u.save()
            ret["added"].append(", ".join(line.values()))
    except Exception as e:
        print("new error: "+e)
        # raise e
    return ret


def add_users_from_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ret = add_users_from_file(request.FILES["file"])
            except TypeError as e:
                return HttpResponse(str(e) + ". Invalid format? file must have 2 columns seperated by a comma: firstname, lastname")
            except Exception as e:
                return HttpResponse(e)
            return HttpResponse("<br>".join(("added: " + ", ".join(ret["added"] or ["-"]), "duplicate: "+", ".join([" ".join((val.values())) for val in ret["duplicate"] or ["-"]]))))
    else:
        form = UploadFileForm()
    return render(request, "kasseBE/add_users.html", {"form": form})


def ordered_today(self, pk):
    obj = get_object_or_404(User, code=pk)
    date_field_name = 'order_date'
    filter_kwargs = {}
    today = now()
    filter_kwargs['%s__day' % date_field_name] = today.day
    filter_kwargs['%s__month' % date_field_name] = today.month
    filter_kwargs['%s__year' % date_field_name] = today.year
    cal = obj.order_set.all().filter(**filter_kwargs)
    if (cal):
        OrderSerializer(cal.first()).data
    else:
        return {}


class DateValidator(UniqueForDateValidator):
    message = _("The user already ordered today. ")
    message = "Der Kunde hat heute bereits bestellt."

    # überschreiben von UniqueForDateValidator::BaseUniqueForValidator::__call__ da wir die order in der response haben wollen.
    # theoretisch könnten wir nur die message ändern, aber das wäre schwieriger im frontend zu parsen.
    def __call__(self, attrs, serializer):
        # Determine the underlying model field names. These may not be the
        # same as the serializer field names if `source=<>` is set.
        field_name = serializer.fields[self.field].source_attrs[-1]
        date_field_name = serializer.fields[self.date_field].source_attrs[-1]

        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(
            attrs, queryset, field_name, date_field_name)
        queryset = self.exclude_current_instance(
            attrs, queryset, serializer.instance)
        if qs_exists(queryset):
            message = self.message.format(date_field=self.date_field)
            raise ValidationError({
                self.field: message,
                "order":  OrderHyperlinkSerializer(queryset.first(), context={'request': None}).data
            }, code='unique')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'userID', 'order_date', 'ordered_item', 'tax']
        validators = [
            DateValidator(
                queryset=Order.objects.all(),
                field='userID', date_field='order_date'
            )
        ]
    order_date = serializers.DateTimeField(read_only=True, default=now)


class OrderViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class UserSerializer(serializers.ModelSerializer):
    def get_last_ordered(self, obj: User):
        if (obj.order_set.all()):
            data = OrderSerializer(obj.order_set.latest('order_date')).data
            data.pop("userID")
            return data
        else:
            return None

    class Meta:
        model = User
        fields = fields = ['firstname', 'lastname',
                           'code', 'active', 'last_ordered']
    last_ordered = serializers.SerializerMethodField()
    firstname = serializers.CharField(write_only=True)
    lastname = serializers.CharField(write_only=True)
    # enddate = serializers.DateTimeField(write_only=True)


class UserViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=["GET"])
    def barcode(self, request, pk=None):
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
        cal = obj.order_set.all().filter(**filter_kwargs)
        if (cal):
            return Response(OrderSerializer(cal.first()).data)
        else:
            return Response({})


class OrderHyperlinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ['url', 'userID', 'order_date', 'ordered_item', 'tax']
        validators = [
            DateValidator(
                queryset=Order.objects.all(),
                field='userID', date_field='order_date'
            )
        ]
    order_date = serializers.DateTimeField(read_only=True, default=now)


class OrderBillSerializer(serializers.ModelSerializer):
    def get_total(self, obj: OrderBill):
        return sum(order.ordered_item for order in obj.order_set.all())

    def get_total_with_tax(self, obj: OrderBill):
        return sum(order.ordered_item+(order.ordered_item*order.tax/100) for order in obj.order_set.all())

    class Meta:
        model = OrderBill
        fields = ['month', 'order_set', 'total', 'total_with_tax']
    order_set = OrderSerializer(many=True)
    total = serializers.SerializerMethodField()
    total_with_tax = serializers.SerializerMethodField()


class OrderBillViewSet(viewsets.ReadOnlyModelViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = OrderBill.objects.all()
    serializer_class = OrderBillSerializer

    @action(detail=False, methods=["GET"])
    def latest(self, request):
        return Response(self.get_serializer(self.queryset.latest('month')).data)
