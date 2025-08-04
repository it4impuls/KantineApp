from django.contrib import admin
from django.utils.html import format_html, format_html_join
from .models import User, Order
from .views import get_barcode
# Register your models here.


admin.site.register(Order)



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    
    
    model = User
    empty_value_display = "-empty-"
    search_fields = ["firstname", "lastname", "code", "active",]
    list_display = ["firstname", "lastname", "code", "active", "enddate" ]
    readonly_fields = ["barcode"]
    # fields = [barcode]
    # list_display = []
    # list_display = ["barcode"]
    
    @admin.display(description="barcode")
    def barcode(self, obj):
        html = format_html('<img src="{}/{}/{}" />', "users", obj.pk, "barcode")
        print(html)
        return html
        bc = get_barcode(obj.pk)
        bc.seek(0)
        return bc

# admin.site.register(UserAdmin)