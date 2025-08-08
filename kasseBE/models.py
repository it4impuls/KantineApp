from django.db import models
from django.utils.timezone import localdate, now
from datetime import date
from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from django.utils.translation import gettext as _


def in4yrs() -> date:
    return now() + relativedelta(years=4)

class User(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    code  = models.AutoField(primary_key=True)
    active = models.BooleanField(default=True)
    enddate = models.DateField(default=in4yrs)

def is_active(value:User):
    if (not value.active):
        raise serializers.ValidationError( "Der Benutzer ist nicht Aktiv")# _("User is not active"))

class Order(models.Model):
    class Tax(models.IntegerChoices):
        TAKEOUT = 19
        INHOUSE = 7

    order_date = models.DateTimeField(auto_now=True)
    userID = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, unique_for_date="order_date", validators=[is_active])
    ordered_item = models.DecimalField(decimal_places=2, max_digits=6)
    tax = models.IntegerField(choices=Tax)