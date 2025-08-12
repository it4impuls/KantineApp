from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from django.http.response import HttpResponse
from .models import User, Order, OrderBill
from datetime import date, timedelta
from django.utils.translation import gettext_lazy as _
from csv import DictWriter
from .views import OrderSerializer
# Register your models here.


class CustomDateFieldListFilter(DateFieldListFilter):
    # überschreiben der DateFieldListFilter::__init__ um mehr links hinzuzufügen.
    def __init__(self, field, request, params, model, model_admin, field_path):
        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # field is a models.DateField
            today = now.date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        super().__init__(field, request, params, model, model_admin, field_path)
        self.links += ((
            _("This week"),
            {
                self.lookup_kwarg_since: week_start,
                self.lookup_kwarg_until: week_end,
            },
        ),)


@admin.action(description="Export selected as csv")
def export_orders(modeladmin, request, queryset):
    if not queryset:
        return
    data = [OrderSerializer(a).data for a in queryset]
    if len(data) == 0:
        return
    headers = data[0].keys()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Orders.csv"'
    wr = DictWriter(response, headers)
    wr.writerows(data)
    return response


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["firstname", "lastname", "code"]
    list_display = ["firstname", "lastname", "code", "active", "enddate"]
    readonly_fields = ["barcode"]

    @admin.display(description="barcode")
    def barcode(self, obj):
        return format_html('<img src="/{}/{}/{}" />', "users", obj.pk, "barcode")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = list_display = list_display_links = [
        "order_date", "userID__code", "ordered_item", "tax"]
    list_filter = (('order_date', CustomDateFieldListFilter),)
    actions = [export_orders]
    # change_list_template = "admin/order_change_list.html"


class OrderInline(admin.TabularInline):
    @admin.display(description="user")
    def user(self, obj):
        return obj.userID.code
    model = Order
    readonly_fields = ["user", "order_date", "ordered_item", "tax"]
    exclude = ["userID"]
    extra = 1


def calc_total(obj: OrderBill):
    return sum(order.ordered_item for order in obj.order_set.all())


def calc_total_taxed(obj: OrderBill):
    return sum(order.ordered_item+(order.ordered_item*order.tax/100) for order in obj.order_set.all())


@admin.register(OrderBill)
class OrderBillAdmin(admin.ModelAdmin):

    search_fields = list_display = list_display_links = readonly_fields = [
        'month', 'total', 'total_with_tax']
    ordering = ('-month',)
    inlines = [OrderInline]

    @admin.display(description="total")
    def total(self, obj: OrderBill):
        today = date.today()
        if obj.month < today:
            if not obj.cached_total:
                obj.cached_total = calc_total(obj)
                obj.save()
            return obj.cached_total
        return calc_total(obj)

    @admin.display(description="total with tax")
    def total_with_tax(self, obj: OrderBill):
        today = date.today()
        if obj.month < today:
            if not obj.cached_taxed_total:
                obj.cached_taxed_total = calc_total_taxed(obj)
                obj.save()
            return obj.cached_taxed_total
        return calc_total_taxed(obj)
