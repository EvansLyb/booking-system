# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from typing import Any, Dict
from django import forms
from django.forms import Form
from django.core.exceptions import ValidationError


class LockForm(Form):
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "placeholder": "Date",
                "class": "form-control datepicker"
            },
        ))
    from_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "From",
                "class": "form-control fromtimepicker"
            },
            format="%H:%M"
        ))
    to_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(
            attrs={
                "placeholder": "To",
                "class": "form-control totimepicker"
            },
            format="%H:%M"
        ))
    
    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        from_time = cleaned_data.get('from_time')
        to_time = cleaned_data.get('to_time')
        if from_time == to_time:
            raise ValidationError('Please set a different time')
