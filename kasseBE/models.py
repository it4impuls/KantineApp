from django.db import models
from django.utils.timezone import localdate, now
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
# Create your models here.

def in4yrs() -> date:
    return now() + relativedelta(years=4)

class User(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    code  = models.CharField(max_length=50, unique=True, primary_key=True)
    active = models.BooleanField()
    enddate = models.DateField(default=in4yrs)

class Order(models.Model):
    class Tax(models.IntegerChoices):
        TAKEOUT = 19
        INHOUSE = 7

    
    order_date = models.DateTimeField(auto_now_add=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE, unique_for_date="order_date")
    ordered_item = models.DecimalField(decimal_places=2, max_digits=6)
    tax = models.IntegerField(choices=Tax)