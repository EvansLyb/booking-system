# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.urls import path, re_path

from .views import get_facility_list, get_stadium_list

urlpatterns = [
    path('/stadium/list', get_stadium_list, name='get_stadium_list'),
    path('/facility/list', get_facility_list, name='get_facility_list'),
]
