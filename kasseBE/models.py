from django.db import models
from django.utils.timezone import now
from datetime import date
from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from django.utils.translation import gettext as _


# def current_bill() -> int:
#     thismonth = date.today().replace(day=1)+relativedelta(months=1, days=-1)
#     orders = OrderBill.objects.all().filter(month=thismonth)
#     if (orders):
#         bill = orders.first()
#     else:
#         bill = OrderBill(month=thismonth)
#         bill.save()

#     return bill.pk


def in4yrs() -> date:
    return now() + relativedelta(years=4)


class User(models.Model):
    class Meta:
        verbose_name = 'Kunde'
        verbose_name_plural = 'Kunde'
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    code = models.AutoField(primary_key=True)
    active = models.BooleanField(default=True)
    enddate = models.DateField(default=in4yrs)


def is_active(value: User):
    if (not value.active):
        # _("User is not active"))
        raise serializers.ValidationError("Der Benutzer ist nicht Aktiv")
    if (value.enddate < date.today()):
        raise serializers.ValidationError(
            "Der Benutzer hat sein end-datum erreicht.")


# class OrderBill(models.Model):
#     class Meta:
#         verbose_name = 'Abrechnung'
#         verbose_name_plural = 'Abrechnungen'
#     month = models.DateField()
#     cached_total = models.DecimalField(
#         decimal_places=2, max_digits=6, null=True)
#     cached_taxed_total = models.DecimalField(
#         decimal_places=2, max_digits=6, null=True)


class Order(models.Model):
    class Meta:
        verbose_name = 'Bestellung'
        verbose_name_plural = 'Bestellungen'

    order_date = models.DateTimeField(auto_now=True)
    userID = models.ForeignKey(User, on_delete=models.PROTECT,
                               unique_for_date="order_date", validators=[is_active])
    ordered_item = models.DecimalField(decimal_places=2, max_digits=6)
    tax = models.IntegerField(choices={7: "7%", 19: "19%"})
    # bill = models.ForeignKey(OrderBill, default=current_bill, on_delete=models.PROTECT, limit_choices_to={
    #                          "month__month": date.today().month, "month__year": date.today().year})
