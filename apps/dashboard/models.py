# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

from apps.authentication.models import Account

# Create your models here.

class Stadium(models.Model):
    name = models.CharField('name', max_length=256, blank=False)
    longitude = models.FloatField('location - longitude')
    latitude = models.FloatField('location - latitude')
    location = models.CharField('location', max_length=1024, blank=True)

class Facility(models.Model):
    name = models.CharField('name', max_length=256, blank=False)
    cover_image = models.ImageField('cover name', upload_to="facility/")
    description = RichTextUploadingField('description')


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
    low_time_price = models.FloatField()
    high_time_price = models.FloatField()
    separation_timing = models.TimeField()


class LockInfo(models.Model):
    facility_id = models.BigIntegerField('facility_id', blank=False)
    date = models.DateField('date')
    slot = models.CharField('slot', max_length=255, blank=False)  # just for display


class Freeze(models.Model):
    facility_id = models.BigIntegerField('facility_id', blank=False)
    date = models.DateField('date')
    court_type = models.CharField(max_length=255, choices=CourtType.choices, default=None, null=True, blank=True)
    is_lock = models.BooleanField(default=False)
    is_order = models.BooleanField(default=False)
    time = models.TimeField()  # start time, slot=30min


class Order(models.Model):
    pass
