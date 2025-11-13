from django.conf import settings
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from django.utils import timezone, dateparse
from django.db import models
from django.http.response import HttpResponse
from django.db.models import Q
from .models import User, Order
from datetime import date, timedelta
from django.utils.translation import gettext_lazy as _
from csv import DictWriter, writer
from .views import OrderSerializer, UserSerializer, get_barcode
import zipfile
from io import BytesIO


class InputFilter(admin.SimpleListFilter):
    # from https://hakibenita.com/how-to-add-a-text-filter-to-django-admin
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter. This will prevent facets from working
        return (("",),)

    def choices(self, changelist):
        # Grab only the "all" option.
        # empty lookups() results in exception if add_facets are active
        # changelist.add_facets = False
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class UIDFilter(InputFilter):
    title = "Monat (yyyy-mm)"
    parameter_name = "order_date"

    def queryset(self, request, queryset):
        if self.value() is not None:
            try:
                # try convert other formats into iso
                val = self.value().replace(".", "-").replace("/", "-")
                if (val.count("-") == 1):
                    d = dateparse.parse_date(val+"-01")
                else:
                    d = dateparse.parse_date(val)
            except ValueError as e:
                self.used_parameters[self.parameter_name] = _(str(e))
                return queryset.none()
            if not d:
                self.used_parameters[self.parameter_name] = "invalid formatting"
                return queryset.none()

            return queryset.filter(
                Q(order_date__month=d.month, order_date__year=d.year)
            )


class CustomDateFieldListFilter(DateFieldListFilter):
    # TODO: export past months. Paginators?
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
        # Monday=0, Sunday=6
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # last day last month
        last_month_end = today-timedelta(days=today.day)
        last_month_start = last_month_end.replace(day=1)

        super().__init__(field, request, params, model, model_admin, field_path)
        self.links += ((
            _("This week"),
            {
                self.lookup_kwarg_since: week_start,
                self.lookup_kwarg_until: week_end,
            },
        ), (
            _("Last month"),
            {
                self.lookup_kwarg_since: last_month_start,
                self.lookup_kwarg_until: last_month_end,
            },
        ))


def changeStrEncoding(entry: dict, encoding: str):
    # hacky solution to unclean db data
    stripped = entry.replace('\ufeff', '')
    return stripped.encode(
        settings.DEFAULT_CHARSET).decode(encoding)


@admin.action(description=_("Export barcodes as .zip"))
def export_user_Barcodes(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="Barcodes.zip"'
    try:
        # s = BytesIO()
        with zipfile.ZipFile(response, "w") as zf:
            for user in queryset:
                assert type(user) == User
                zf.writestr(
                    "_".join((user.lastname, user.firstname))+".svg", get_barcode(str(user.code)).getvalue())
        # zf.open("barcodes.zip")
        # s.seek(0)
        # return FileResponse(s, filename="barcodes.zip", as_attachment=True)
    except TypeError as e:
        return HttpResponse(str(e) + ". Invalid format? file must have 2 columns seperated by a comma: firstname, lastname")
    except Exception as e:
        return HttpResponse(e)
    return response


@admin.action(description=_("Export selection as csv"))
def export_users(modeladmin, request, queryset):
    if not queryset:
        return

    data = [UserSerializer(a).data for a in queryset]
    if len(data) == 0:
        return
    headers = data[0].keys()
    response = HttpResponse(
        content_type='text/csv; charset='+settings.EXPORT_ENCODING)
    response['Content-Disposition'] = 'attachment; filename="Teilnehmer.csv"'
    wr = DictWriter(response, headers, dialect='excel',
                    delimiter=';', lineterminator='\r\n')
    for line in data:
        try:
            wr.writerow(line)
        except UnicodeEncodeError as e:
            response.write(changeStrEncoding(e.object, e.encoding))
        except Exception as e:
            ...
    return response


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["firstname", "lastname", "code"]
    list_display = ["firstname", "lastname", "code", "active"]
    readonly_fields = ["barcode"]
    actions = [export_user_Barcodes, export_users]

    @admin.display(description="barcode")
    def barcode(self, obj):
        # link zum barcode svg (/users/pk/barcode)
        return format_html('<img src="/{}/{}/{}" />', "users", obj.pk, "barcode")


@admin.action(description=_("Export selection as csv"))
def export_orders(modeladmin, request, queryset):
    if not queryset:
        return

    data = [OrderSerializer(a).data for a in queryset]
    if len(data) == 0:
        return
    headers = data[0].keys()
    response = HttpResponse(
        content_type='text/csv; charset='+settings.EXPORT_ENCODING)
    response['Content-Disposition'] = 'attachment; filename="Orders.csv"'
    wr = DictWriter(response, headers, dialect='excel',
                    delimiter=';', lineterminator='\r\n')
    # required for non-dict writing
    w = writer(response, dialect='excel', delimiter=';', lineterminator='\r\n')
    # w.writerow(("Bestellungs ID", "Kunde", "Zeit", "Menu", "Steuer"))
    wr.writeheader()
    for line in data:
        try:
            wr.writerow(line)
        except UnicodeEncodeError as e:
            response.write(changeStrEncoding(e.object, e.encoding))

    # write some extra data, IE sums
    w.writerow("")
    w.writerow((
        "7%: ", sum(entry.ordered_item for entry in queryset.filter(tax=7))))
    w.writerow(
        ("19%: ", sum(entry.ordered_item for entry in queryset.filter(tax=19))))
    w.writerow(("Total: ", sum(entry.ordered_item for entry in queryset)))

    return response


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = list_display = list_display_links = [
        "order_date", "userID__code", "ordered_item", "tax"]
    list_filter = (('order_date', CustomDateFieldListFilter),
                   UIDFilter,
                   'ordered_item', 'tax')
    actions = [export_orders]
    # show_facets = admin.ShowFacets.ALWAYS
    # change_list_template = "admin/order_change_list.html"


class OrderInline(admin.TabularInline):
    @admin.display(description="user")
    def user(self, obj: Order):
        return obj.userID.code
    model = Order
    readonly_fields = ["user", "order_date", "ordered_item", "tax"]
    exclude = ["userID"]
    extra = 1
