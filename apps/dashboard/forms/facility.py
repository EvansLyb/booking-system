# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django import forms
from django.forms import ModelForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from apps.dashboard.models import Facility, FacilityCoverImage


class FacilityForm(ModelForm):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name",
                "class": "form-control",
                "autocomplete": "off"
            }
        ))
    # cover_image_list = forms.ImageField(
    #     required=True,
    #     label=False,
    #     widget=forms.ClearableFileInput(
    #         attrs={
    #             "placeholder": "Cover Image List",
    #             "class": "file-loading",
    #             "multiple": True
    #         }
    #     ))
    description = forms.CharField(
        required=False,
        widget=CKEditorUploadingWidget(
            attrs={
                "placeholder": "description",
                "class": "form-control",
                "autocomplete": "off"
            }
        ))

    class Meta:
        model = Facility
        fields = '__all__'

    # def save(self, commit=True):
    #   facility = super(Facility, self).save(commit=False)
    #   facility.description = self.cleaned_data.get('description', '')
    #   if commit:
    #     facility.save()
    #   return facility
