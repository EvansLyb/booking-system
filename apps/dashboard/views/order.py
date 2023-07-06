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
from django.db.models import Sum, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse, Http404
from django.template import loader
from django.core.paginator import Paginator

import math
import uuid
import requests
import json
import datetime

from apps.dashboard.models import Order, Facility, Bill, OrderStatus
from apps.apis.models import User
from apps.dashboard.forms.order import OrderFilterForm


NUMBER_OF_PAGE = 25

class OrderListView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        context = {'segment': 'order'}

        query_from_date = request.GET.get('from_date', None)
        query_to_date = request.GET.get('to_date', None)
        phone_number = request.GET.get('phone_number', None)
        query_status_list = request.GET.getlist('status', [])

        # filter
        query = Q()
        if query_from_date and query_to_date:
            query_from_date_obj = datetime.datetime.strptime(query_from_date, '%Y-%m-%d')
            query_to_date_obj = datetime.datetime.strptime(query_to_date, '%Y-%m-%d')
            query.add(Q(date__gte=query_from_date_obj, date__lte=query_to_date_obj), Q.AND)
        if query_from_date and not query_to_date:
            query_from_date_obj = datetime.datetime.strptime(query_from_date, '%Y-%m-%d')
            query.add(Q(date__gte=query_from_date_obj), Q.AND)
        if query_to_date and not query_from_date:
            query_to_date_obj = datetime.datetime.strptime(query_to_date, '%Y-%m-%d')
            query.add(Q(date__lte=query_to_date_obj), Q.AND)
        if phone_number:
            user = User.objects.filter(phone_number=phone_number).first()
            user_id = user.id if user else None
            query.add(Q(user_id=user_id), Q.AND)
        if len(query_status_list) > 0:
            query1 = Q()
            for query_status in query_status_list:
                query1.add(Q(status=query_status), Q.OR)
            query.add(query1, Q.AND)
        order_list = Order.objects.filter(query)

        paginator = Paginator(order_list.order_by('-updated_at'), NUMBER_OF_PAGE)
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


class OrderDetailsView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, order_no=None):
        context = {'segment': 'order'}
        if not order_no:
            raise Http404
        
        order = Order.objects.filter(order_no=order_no).first()
        if not order:
            raise Http404

        context['order'] = order

        bill_list = Bill.objects.filter(order_id=order.id).order_by('created_at')
        context['bill_list'] = bill_list

        html_template = loader.get_template('dashboard/order-details.html')
        return HttpResponse(html_template.render(context, request))


class OrderStatusView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, order_no=None):
        if not order_no:
            raise Http404
        
        order = Order.objects.filter(order_no=order_no).first()
        if not order:
            raise Http404

        json_data = json.loads(request.body)
        status = json_data.get('status', '')
        if status != OrderStatus.ACCEPTED and status != OrderStatus.REJECTED:
            raise Exception("Status does not exist")
        
        order.status = status
        order.save()
        return JsonResponse({}, safe=False, status=201)

