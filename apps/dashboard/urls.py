# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.urls import path, re_path
from apps.dashboard import views_old
from apps.dashboard.views_old import AccountListView, StadiumListView, StadiumView, AccountView, PriceView, PriceListView
from .views.lock import LockView, get_lock_info
from .views.facility import FacilityListView, FacilityView, FacilityCoverImageView, get_cover_image_list, download_cover_image_by_url, get_upload_image_info, delete_cover_image_by_file_id
from .views.order import (
    OrderListView,
    OrderDetailsView,
    OrderStatusView,
    OrderView,
    update_phone_number as update_order_phone_number,
    update_facility as update_order_facility,
    update_date as update_order_date,
    update_court_type as update_order_court_type,
    update_time as update_order_time,
    update_status as update_order_status,
    update_remark as update_order_remark,
    update_price as update_order_price
)

urlpatterns = [

    path('/account/list', AccountListView.as_view(), name='dashboard_account_list'),
    path('/account', AccountView.as_view()),
    path('/account/<int:id>', AccountView.as_view(), name="dashboard_account"),
    path('/stadium/list', StadiumListView.as_view(), name='dashboard_stadium_list'),
    path('/stadium', StadiumView.as_view()),
    path('/stadium/<int:id>', StadiumView.as_view(), name='dashboard_stadium'),
    path('/facility/list', FacilityListView.as_view(), name='dashboard_facility_list'),
    path('/facility', FacilityView.as_view()),
    path('/facility/<int:id>', FacilityView.as_view(), name='dashboard_facility'),
    path('/facility/<int:fid>/price/list', PriceListView.as_view(), name='dashboard_facility_price_list'),
    path('/facility/<int:fid>/price', PriceView.as_view()),
    path('/facility/<int:fid>/price/<int:pid>', PriceView.as_view(), name='dashboard_facility_price'),
    path('/facility/<int:fid>/get-cover-image-list', get_cover_image_list, name='dashboard_facility_get_cover_image_list'),
    path('/facility/<int:fid>/lock', LockView.as_view()),
    path('/facility/<int:fid>/unlock/<int:lid>', LockView.as_view()),
    path('/facility/<int:fid>/lock/info', get_lock_info, name='dashboard_lock_info'),
    path('/facility/<int:fid>/cover-image', FacilityCoverImageView.as_view()),
    path('/facility/download-cover-image-by-url', download_cover_image_by_url, name='dashboard_download_cover_image_by_url'),
    path('/facility/get-upload-file-info', get_upload_image_info),
    path('/facility/delete-cover-image-by-file-id', delete_cover_image_by_file_id),
    path('/order/list', OrderListView.as_view()),
    path('/order/<str:order_no>/details', OrderDetailsView.as_view()),
    path('/order/<str:order_no>', OrderView.as_view()),
    path('/order/<str:order_no>/status', OrderStatusView.as_view()),
    path('/order/<str:order_no>/update-phone-number', update_order_phone_number),
    path('/order/<str:order_no>/update-facility', update_order_facility),
    path('/order/<str:order_no>/update-date', update_order_date),
    path('/order/<str:order_no>/update-court-type', update_order_court_type),
    path('/order/<str:order_no>/update-time', update_order_time),
    path('/order/<str:order_no>/update-status', update_order_status),
    path('/order/<str:order_no>/update-price', update_order_price),
    path('/order/<str:order_no>/update-remark', update_order_remark),

    # # Matches any html file
    re_path(r'^.*\.*', views_old.pages, name='dashboard_pages'),

]
