# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.db import models


class User(models.Model):
    open_id = models.CharField('open_id', max_length=256, blank=False)
    phone_number = models.CharField('phone_number', max_length=32, default='')
    nick_name = models.CharField('nick_name', max_length=255, default='')
