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
    cover_image = forms.ImageField(
        required=True,
        label=False,
        widget=forms.FileInput(
            attrs={
                "placeholder": "Cover Image",
                "class": "file-loading"
            }
        ))
    description = forms.CharField(
        required=False,
        widget=CKEditorUploadingWidget(
            attrs={
                "placeholder": "description",
                "class": "form-control"
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
