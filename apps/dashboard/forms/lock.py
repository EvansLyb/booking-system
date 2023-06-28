# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from typing import Any, Dict
from django import forms
from django.forms import Form
from django.core.exceptions import ValidationError

from apps.dashboard.models import LockType


class LockForm(Form):
    lock_type = forms.ChoiceField(
        required=True,
        choices=LockType.choices,
        widget=forms.Select(
            attrs={
                "placeholder": "Lock Type",
                "class": "form-control", 
            }
        ))
    from_date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "placeholder": "From",
                "class": "form-control fromdatepicker",
                "autocomplete": "off"
            },
        ))
    to_date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "placeholder": "To",
                "class": "form-control todatepicker",
                "autocomplete": "off"
            },
        ))
    from_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "From",
                "class": "form-control fromtimepicker",
                "autocomplete": "off"
            },
            format="%H:%M"
        ))
    to_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "To",
                "class": "form-control totimepicker",
                "autocomplete": "off"
            },
            format="%H:%M"
        ))

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        from_time = cleaned_data.get('from_time')
        to_time = cleaned_data.get('to_time')
        lock_type = cleaned_data.get('lock_type')
        if (lock_type == LockType.REPEAT) and from_time >= to_time:
            raise ValidationError('Invalid time')
        if (from_date == to_date or lock_type == LockType.REPEAT) and from_time == to_time:
            raise ValidationError('Please set a different time')
