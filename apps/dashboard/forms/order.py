# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from typing import Any, Dict
from django import forms
from django.forms import Form
from django.core.exceptions import ValidationError

from apps.dashboard.models import Order, OrderStatus


class OrderFilterForm(Form):
    pass