# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django import forms
from django.forms import ModelForm

from apps.dashboard.models import Stadium


class StadiumForm(ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name",
                "class": "form-control"
            }
        ))
    longitude = forms.FloatField(
        required=True,
        min_value=0,
        initial=0,
        widget=forms.TextInput(
            attrs={
                "placeholder": "location - longitude",
                "class": "form-control"
            }
        ))
    latitude = forms.FloatField(
        required=True,
        min_value=0,
        initial=0,
        widget=forms.TextInput(
            attrs={
                "placeholder": "location - latitude",
                "class": "form-control"
            }
        ))
    location = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Location",
                "class": "form-control"
            }
        ))

    class Meta:
        model = Stadium
        fields = '__all__'
