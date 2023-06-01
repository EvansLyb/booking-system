# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import login_view

urlpatterns = [
    path('login', login_view, name="login"),
    # path('register', register_user, name="register"),
    path("logout", LogoutView.as_view(next_page='/login'), name="logout")
]
