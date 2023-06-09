# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

import datetime
from decimal import Decimal


# Create your models here.

class Stadium(models.Model):
    name = models.CharField('name', max_length=256, blank=False)
    longitude = models.FloatField('location - longitude')
    latitude = models.FloatField('location - latitude')
    location = models.CharField('location', max_length=1024, blank=True)
    description = models.TextField('description', blank=True, default='')


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
    full_day_price = models.FloatField()
    normal_hourly_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    peek_hourly_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0), null=True)
    peek_time_from = models.TimeField(null=True)
    peek_time_to = models.TimeField(null=True)


class LockType(models.TextChoices):
    REPEAT = "REPEAT"
    CONTINUOUS = "CONTINUOUS"

class LockInfo(models.Model):
    facility_id = models.BigIntegerField('facility_id', blank=False)
    from_date = models.DateField('from_date', default=datetime.date.today)
    to_date = models.DateField('to_date', default=datetime.date.today)
    slot = models.CharField('slot', max_length=255, blank=False)  # just for display
    operator = models.CharField('operator', max_length=255, blank=True)
    lock_type = models.CharField('lock_type', max_length=255, choices=LockType.choices, default=LockType.REPEAT)


class Freeze(models.Model):
    facility_id = models.BigIntegerField('facility_id', blank=False)
    date = models.DateField('date')
    court_type = models.CharField(max_length=255, choices=CourtType.choices, default=None, null=True, blank=True)
    is_lock = models.BooleanField(default=False)
    """
    - Lock once, increment the count by 1
    - Unlock once, decrement the count by 1.
    """
    lock_count = models.IntegerField('lock_count', default=0)
    is_order = models.BooleanField(default=False)
    time = models.TimeField()  # start time, slot=30min


class Order(models.Model):
    pass
