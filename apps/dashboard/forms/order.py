# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from typing import Any, Dict, Mapping, Optional, Type, Union
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from apps.dashboard.models import Order, OrderStatus, Facility, CourtType


class OrderForm(ModelForm):
    order_no = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off",
                "readonly": True
            }
        ))
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off"
            }
        ))
    facility_id = forms.ChoiceField(
        required=True,
        choices=[(facility.id, facility.name) for facility in Facility.objects.all()],
        widget=forms.Select(
            attrs={
                "class": "form-control",
            },
        ))
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "placeholder": "From",
                "class": "form-control datepicker",
                "autocomplete": "off"
            },
        ))
    court_type = forms.ChoiceField(
        required=True,
        choices=CourtType.choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            },
        ))
    time_list = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off"
            }
        ))
    status = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off",
            }
        ))
    price = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control price-input",
                "autocomplete": "off",
                "readonly": True
            }
        ))
    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "autocomplete": "off"
            }
        ))

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['user_id']
