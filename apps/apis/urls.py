# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.urls import path, re_path

from .views import (
    get_facility_list,
    get_stadium_list,
    check_phone_number,
    bind_phone_number,
    get_price_info,
    get_freeze,
    create_order,
    payment_callback,
    get_order_list,
    get_order_details
)

urlpatterns = [
    path('/stadium/list', get_stadium_list, name='get_stadium_list'),
    path('/facility/list', get_facility_list, name='get_facility_list'),
    path('/phone-number/check', check_phone_number, name='check_phone_number'),
    path('/phone-number/bind', bind_phone_number, name='bind_phone_number'),
    path('/get-price-info/<int:fid>', get_price_info),
    path('/get-freeze', get_freeze),
    path('/create-order', create_order),
    path('/pay/callback', payment_callback),
    path('/order-list', get_order_list),
    path('/order/<int:oid>', get_order_details),
]
