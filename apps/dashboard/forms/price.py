# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django import forms
from django.forms import ModelForm

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
                "class": "form-control datetimepicker",
                "autocomplete": "off"
            },
            format="%H:%M"
        ))
    closing_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "Closing Time",
                "class": "form-control datetimepicker"
            },
            format="%H:%M"
        ))
    full_day_price = forms.FloatField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Full Day Price",
                "class": "form-control price-input",
                "MAXLENGTH": "10",
            }
        )
    )
    low_time_price = forms.FloatField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Low Time Price",
                "class": "form-control price-input",
                "MAXLENGTH": "10",
            }
        )
    )
    high_time_price = forms.FloatField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "High Time Price",
                "class": "form-control price-input",
                "MAXLENGTH": "10",
            }
        )
    )
    separation_timing = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "Separation Timing",
                "class": "form-control datetimepicker"
            },
            format="%H:%M"
        ))

    class Meta:
        model = Price
        fields = ('court_type', 'day_type', 'opening_time', 'closing_time', 'full_day_price', 'low_time_price', 'high_time_price', 'separation_timing')
        # fields = '__all__'
