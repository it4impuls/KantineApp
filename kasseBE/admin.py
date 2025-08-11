from django.contrib import admin
from django.utils.html import format_html
from .models import User, Order, OrderBill
from datetime import date
# Register your models here.


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
