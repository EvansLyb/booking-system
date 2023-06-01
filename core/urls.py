# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.contrib import admin
from django.urls import path, re_path, include  # add this
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.auth.decorators import login_required
from ckeditor_uploader.views import upload

from core import settings

urlpatterns = [
    # path('admin/', admin.site.urls),          # Django admin route
    path("", include("apps.authentication.urls")), # Auth routes - login / register

    # ADD NEW Routes HERE

    # Leave `Dashboard.Urls` as last the last line
    path("dashboard", include("apps.dashboard.urls"), name="dashboard"),

    # For Media
    re_path(r'^media/(?P<path>.*)$', serve, kwargs={'document_root': settings.MEDIA_ROOT}),

    # For rich text file uploader
    path('ckeditor/upload/', login_required(upload), name='ckeditor_upload'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]
