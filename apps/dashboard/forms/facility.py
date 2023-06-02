# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django import forms
from django.forms import ModelForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from apps.dashboard.models import Facility


class FacilityForm(ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name",
                "class": "form-control"
            }
        ))
    stadium = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Stadium Name",
                "class": "form-control"
            }
        ))
    cover_image = forms.ImageField(
        required=True,
        label=False,
        widget=forms.FileInput(
            attrs={
                "placeholder": "Cover Image",
                "class": "file-loading"
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
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Location",
                "class": "form-control"
            }
        ))
    description = forms.CharField(
        required=True,
        widget=CKEditorUploadingWidget(
            attrs={
                "placeholder": "description",
                "class": "form-control"
            }
        ))
    # description = RichTextUploadingField()

    class Meta:
        model = Facility
        fields = '__all__'

    # def save(self, commit=True):
    #   account = super(Facility, self).save(commit=False)
    #   account.email = self.cleaned_data.get('email')
    #   account.phone_number = self.cleaned_data.get('phone_number')
    #   account.is_super_admin = self.cleaned_data.get('is_super_admin')
    #   if commit:
    #     account.save()
    #   return account
