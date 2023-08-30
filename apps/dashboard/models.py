# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

import datetime
from decimal import Decimal

from apps.apis.models import User


class Stadium(models.Model):
    name = models.CharField('name', max_length=256, blank=False)
    longitude = models.FloatField('location - longitude')
    latitude = models.FloatField('location - latitude')
    location = models.CharField('location', max_length=1024, blank=True)
    description = models.TextField('description', blank=True, default='')


class StadiumImage(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.SET_NULL, null=True, blank=True)
    file_path = models.CharField('file_path', max_length=2048, blank=False, default="")
    file_id = models.CharField('file_id', max_length=2048, blank=False, default="")


class Facility(models.Model):
    name = models.CharField('name', max_length=256, blank=False)
    description = RichTextUploadingField('description', default='', blank=True)


class FacilityCoverImage(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    file_path = models.CharField('file_path', max_length=2048, blank=False, default="")
    file_id = models.CharField('file_id', max_length=2048, blank=False, default="")


# Facility Court Type
class CourtType(models.TextChoices):
    FULL = "FULL"
    HALF = "HALF"
    QUARTER = "QUARTER"


class DayType(models.TextChoices):
    WEEKDAY = "WEEKDAY"
    WEEKEND = "WEEKEND"


class Price(models.Model):
    facility_id = models.BigIntegerField('facility_id', blank=False)
    court_type = models.CharField(max_length=255, choices=CourtType.choices, default=CourtType.FULL)
    day_type = models.CharField(max_length=255, choices=DayType.choices, default=DayType.WEEKDAY)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    full_day_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0), null=True)
    normal_hourly_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    peek_hourly_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0), null=True)
    peek_time_from = models.TimeField(null=True)
    peek_time_to = models.TimeField(null=True)


class LockType(models.TextChoices):
    REPEAT_EVERYDAY = "REPEAT EVERYDAY"
    REPEAT_MONDAY = "REPEAT MONDAY"
    REPEAT_TUESDAY = "REPEAT TUESDAY"
    REPEAT_WEDNESDAY = "REPEAT WEDNESDAY"
    REPEAT_THURSDAY = "REPEAT THURSDAY"
    REPEAT_FRIDAY = "REPEAT FRIDAY"
    REPEAT_SATURDAY = "REPEAT SATURDAY"
    REPEAT_SUNDAY = "REPEAT SUNDAY"
    CONTINUOUS = "CONTINUOUS"

class LockInfo(models.Model):
    facility_id = models.BigIntegerField('facility_id', blank=False)
    from_date = models.DateField('from_date', default=datetime.date.today)
    to_date = models.DateField('to_date', default=datetime.date.today)
    slot = models.CharField('slot', max_length=255, blank=False)  # just for display
    operator = models.CharField('operator', max_length=255, blank=True)
    lock_type = models.CharField('lock_type', max_length=255, choices=LockType.choices, default=LockType.REPEAT_EVERYDAY)


class Freeze(models.Model):
    facility_id = models.BigIntegerField('facility_id', blank=False)
    date = models.DateField('date')
    """
    weights = 1 means this sku already sold out
    - CourtType.FULL = 1
    - CourtType.HALF = 0.5
    - CourtType.QUARTER = 0.25
    """
    weights = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal(0), null=False)
    is_lock = models.BooleanField(default=False)
    """
    - Lock once, increment the count by 1
    - Unlock once, decrement the count by 1.
    """
    lock_count = models.IntegerField('lock_count', default=0)
    is_order = models.BooleanField(default=False)
    time = models.TimeField()  # start time


class OrderStatus(models.TextChoices):
    PENDING_PAYMENT = "Pending Payment"
    PENDING_CONFIRMATION = "Pending Confirmation"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class Order(models.Model):
    order_no = models.CharField('order_no', max_length=64, null=False)
    facility_id = models.BigIntegerField('facility_id', blank=False)
    user_id = models.BigIntegerField('user_id', blank=False, null=False)
    phone_number = models.CharField('phone_number', max_length=32, default='')
    status = models.CharField(max_length=255, choices=OrderStatus.choices, default=OrderStatus.PENDING_PAYMENT)
    date = models.DateField('date')
    court_type = models.CharField(max_length=255, choices=CourtType.choices, null=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0), null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    remark = models.CharField(max_length=2048, null=True, blank=True)
    user_nick_name = models.CharField(max_length=255, default='')
    time_list = models.CharField(max_length=2048, null=False)  # '["08:30", "12:00", "19:00"]'
    is_full_day = models.BooleanField(default=False)

    @property
    def facility_name(self):
        facility_name = Facility.objects.get(id=self.facility_id).name
        return facility_name


"""
In order to automatically cancel overdue unpaid orders
"""
class UnpaidOrder(models.Model):
    order_id = models.BigIntegerField('order_id', blank=False, null=False)


class BillType(models.TextChoices):
    PAYMENT = "Payment"
    REFUND = "Refund"

class Bill(models.Model):
    order_id = models.BigIntegerField('order_id', blank=False, null=False)
    trade_no = models.CharField(max_length=1024, null=False)
    bill_type = models.CharField(max_length=64, choices=BillType.choices, default=BillType.PAYMENT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0), null=False)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0), null=True)
    transaction_id = models.CharField(max_length=1024, null=True)
    nonce_str = models.CharField(max_length=1024, null=False)
