# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models.expressions import RawSQL
from django.db import connection
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.template import loader
from django.core.paginator import Paginator

import math
import uuid
import requests
import json

from apps.dashboard.models import Order, Facility
from apps.apis.models import User
from apps.dashboard.forms.order import OrderFilterForm


NUMBER_OF_PAGE = 25

class OrderListView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        context = {'segment': 'order'}

        order_list = Order.objects.all().order_by('-updated_at')
        paginator = Paginator(order_list, NUMBER_OF_PAGE)
        # context - page
        current_page = request.GET.get("page")
        context['current_page'] = current_page
        page_count = math.ceil(paginator.count / NUMBER_OF_PAGE)
        context['page_count'] = page_count
        context['page_range'] = range(1, page_count + 1)
        # context - obj
        page_obj = paginator.get_page(current_page)
        context['order_list'] = page_obj

        html_template = loader.get_template('dashboard/order.html')
        return HttpResponse(html_template.render(context, request))
