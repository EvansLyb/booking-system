# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from typing import Any, Dict
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from decimal import Decimal

from apps.dashboard.models import Price, CourtType, DayType


class PriceForm(ModelForm):
    court_type = forms.ChoiceField(
        required=True,
        choices=CourtType.choices,
        widget=forms.Select(
            attrs={
                "placeholder": "Court Type",
                "class": "form-control", 
            }
        )
    )
    day_type = forms.ChoiceField(
        required=True,
        choices=DayType.choices,
        widget=forms.Select(
            attrs={
                "placeholder": "Day Type",
                "class": "form-control", 
            }
        )
    )
    opening_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "Opening Time",
                "class": "form-control datetimepicker openingtimepicker",
                "autocomplete": "off"
            },
            format="%H:%M"
        ))
    closing_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "Closing Time",
                "class": "form-control datetimepicker closingtimepicker",
                "autocomplete": "off"
            },
            format="%H:%M"
        ))
    full_day_price = forms.DecimalField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Full Day Price",
                "class": "form-control price-input",
                "MAXLENGTH": "10",
                "autocomplete": "off"
            }
        )
    )
    normal_hourly_price = forms.DecimalField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Normal Hourly Price",
                "class": "form-control price-input",
                "MAXLENGTH": "10",
                "autocomplete": "off"
            }
        )
    )
    peek_hourly_price = forms.DecimalField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Peek Hourly Price",
                "class": "form-control price-input",
                "MAXLENGTH": "10",
                "autocomplete": "off"
            }
        )
    )
    peek_time_from = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={
                "class": "form-control datetimepicker peektimefrompicker",
                "autocomplete": "off"
            },
            format="%H:%M"
        ))
    peek_time_to = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={
                "class": "form-control datetimepicker peektimetopicker",
                "autocomplete": "off"
            },
            format="%H:%M"
        ))
    
    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        peek_hourly_price = cleaned_data.get('peek_hourly_price', None)
        peek_time_from = cleaned_data.get('peek_time_from', None)
        peek_time_to = cleaned_data.get('peek_time_to', None)
        if (peek_time_from and not peek_time_to) or (peek_time_to and not peek_time_from):
            raise ValidationError('Invalid Peek Time')
        if peek_time_from != None and peek_time_to != None and peek_time_from == peek_time_to:
            raise ValidationError('Peek Time must be a time slot')
        if peek_time_from != None and peek_time_to != None and peek_hourly_price == None:
            raise ValidationError('Invalid Peek Hourly Price')

    class Meta:
        model = Price
        fields = ('court_type', 'day_type', 'opening_time', 'closing_time', 'full_day_price', 'normal_hourly_price', 'peek_hourly_price', 'peek_time_from', 'peek_time_to')
        # fields = '__all__'
