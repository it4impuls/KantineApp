from django.contrib import admin
from django.utils.html import format_html
from .models import User, Order, OrderBill
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["firstname", "lastname", "code"]
    list_display = ["firstname", "lastname", "code", "active", "enddate" ]
    readonly_fields = ["barcode"]
    
    @admin.display(description="barcode")
    def barcode(self, obj):
        return format_html('<img src="/{}/{}/{}" />', "users", obj.pk, "barcode")
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = list_display =list_display_links = ["order_date", "userID__code", "ordered_item", "tax" ]


class OrderInline(admin.TabularInline):
    @admin.display(description="user")
    def user(self, obj):
        return obj.userID.code
    model = Order
    readonly_fields = ["user" ,"order_date", "ordered_item", "tax"]
    exclude = ["userID"]
    extra = 1

@admin.register(OrderBill)
class OrderBillAdmin(admin.ModelAdmin):
    @admin.display(description="total")
    def total(self, obj):
        return sum(order.ordered_item for order in obj.order_set.all())
    @admin.display(description="total with tax")
    def total_with_tax(self, obj):
        return sum(order.ordered_item+(order.ordered_item*order.tax/100) for order in obj.order_set.all())
    search_fields = list_display =list_display_links = ["month"]
    readonly_fields = ['total', 'total_with_tax']
    inlines = [OrderInline]