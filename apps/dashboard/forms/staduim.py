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
                "class": "form-control",
                "autocomplete": "off"
            }
        ))
    longitude = forms.FloatField(
        required=True,
        min_value=0,
        initial=0,
        widget=forms.TextInput(
            attrs={
                "placeholder": "location - longitude",
                "class": "form-control",
                "autocomplete": "off"
            }
        ))
    latitude = forms.FloatField(
        required=True,
        min_value=0,
        initial=0,
        widget=forms.TextInput(
            attrs={
                "placeholder": "location - latitude",
                "class": "form-control",
                "autocomplete": "off"
            }
        ))
    location = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Location",
                "class": "form-control",
                "autocomplete": "off"
            }
        ))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description",
                "class": "form-control",
                "autocomplete": "off"
            }
        ))

    class Meta:
        model = Stadium
        fields = '__all__'
