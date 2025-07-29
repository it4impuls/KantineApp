from django.db import models
from django.utils.timezone import localdate, now
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
# Create your models here.

def in4yrs() -> date:
    return localdate(now() + relativedelta(years=4))

class User(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    code  = models.CharField(max_length=50)
    active = models.BooleanField()
    enddate = models.DateField(default=in4yrs)

class Order(models.Model):
    class Tax(models.IntegerChoices):
        TAKEOUT = 19
        INHOUSE = 7

    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    ordered_item = models.DecimalField(decimal_places=2, max_digits=6)
    tax = models.IntegerField(choices=Tax)