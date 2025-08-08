from django.contrib import admin
from django.utils.html import format_html, format_html_join
from .models import User, Order
from .views import get_barcode
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # model=User
    empty_value_display = "-empty-"
    search_fields = ["firstname", "lastname", "code", "active",]
    list_display = ["firstname", "lastname", "code", "active", "enddate" ]
    readonly_fields = ["barcode"]
    
    @admin.display(description="barcode")
    def barcode(self, obj):
        return format_html('<img src="/{}/{}/{}" />', "users", obj.pk, "barcode")
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # model=Order
    empty_value_display = "-empty-"
    search_fields = list_display =list_display_links = ["order_date", "userID__code", "ordered_item", "tax" ]