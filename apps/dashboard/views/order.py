# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.views import View
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models.expressions import RawSQL
from django.db import transaction
from django.db.models import Sum, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse, Http404
from django.template import loader
from django.core.paginator import Paginator
from django.conf import settings

import math
import uuid
import requests
import json
import datetime
from decimal import Decimal

from apps.dashboard.models import Order, Facility, Bill, BillType, OrderStatus, Freeze
from apps.apis.models import User
from apps.dashboard.forms.order import OrderForm
from utils import util
from utils.sms import send_sms
from utils.url_scheme import generate_scheme
from utils.payment import refund
from utils.order import calc_unpay_amount, freeze, unfreeze


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
            query.add(Q(phone_number=phone_number), Q.AND)
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


class OrderView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, order_no=None):
        if not order_no:
            raise Http404

        order = Order.objects.filter(order_no=order_no).first()
        if not order:
            raise Http404

        order_status_selector = OrderStatus.choices
        current_order_status = order.status

        form = OrderForm(request.POST or None, instance=order)
        html_template = loader.get_template('dashboard/order-form.html')

        # context - bills
        bill_list = Bill.objects.filter(order_id=order.id).order_by('created_at')
        return HttpResponse(html_template.render({
            "form": form,
            "bill_list": bill_list,
            "order_status_selector": order_status_selector,
            "current_order_status": current_order_status,
        }, request))

    def _check_if_time_available(self, time_str, facility_id, date, court_type, is_only_court_type_changed = False, old_court_type = None):
        time_obj = datetime.datetime.strptime(time_str, '%H:%M')
        freeze = Freeze.objects.filter(facility_id=facility_id, date=date, time=datetime.time(hour=time_obj.hour, minute=time_obj.minute)).first()
        if freeze:
            new_freeze_weights = freeze.weights - util.get_freeze_weights_by_court_type(old_court_type) + util.get_freeze_weights_by_court_type(court_type) if is_only_court_type_changed else freeze.weights + util.get_freeze_weights_by_court_type(court_type)
            if new_freeze_weights > 1:
                return '{} {} is not available'.format(date, time_str)
            elif freeze.is_lock and freeze.lock_count > 0:
                return '{} {} is locked'.format(date, time_str)
        return None

    """ === deprecated === """
    def post(self, request, order_no=None):
        if not order_no:
            raise Http404

        order = Order.objects.filter(order_no=order_no).first()
        if not order:
            raise Http404

        order_status_selector = OrderStatus.choices
        current_order_status = order.status
        html_template = loader.get_template('dashboard/order-form.html')

        form = OrderForm(request.POST or None)
        if form.is_valid():
            # phone_number = form.cleaned_data.get('phone_number')
            # facility_id = int(form.cleaned_data.get('facility_id'))
            # date = form.cleaned_data.get('date')
            # court_type = form.cleaned_data.get('court_type')
            # time_list_str = form.cleaned_data.get('time_list')
            # time_list = util.trans_list_str_to_list(time_list_str)
            # new_status = form.cleaned_data.get('status')
            # old_status = order.stats
            # remark = form.cleaned_data.get('remark')

            # # check time_list
            # if (len(time_list) < 1):
            #     form.add_error('time_list', 'At least one')
            #     return HttpResponse(html_template.render({
            #         "form": form,
            #         "order_status_selector": order_status_selector,
            #         "current_order_status": current_order_status,
            #     }, request))

            # facility_changed = facility_id != order.facility_id
            # date_changed = date != order.date
            # court_type_changed = court_type != order.court_type
            # time_list_changed = time_list_str != order.time_list
            # status_changed = new_status != old_status
            # if new_status != OrderStatus.REJECTED:
            #     if facility_changed or date_changed or court_type_changed or time_list_changed or status_changed:
            #         """ === data check === """
            #         if facility_changed or date_changed:
            #             for time_str in time_list:
            #                 error_msg = self._check_if_time_available(time_str, facility_id, date, court_type)
            #                 if error_msg:
            #                     form.add_error(None, error_msg)
            #         else:
            #             for time_str in time_list:
            #                 is_new_time = time_str not in util.trans_list_str_to_list(order.time_list)
            #                 if is_new_time:
            #                     error_msg = self._check_if_time_available(time_str, facility_id, date, court_type)
            #                     if error_msg:
            #                         form.add_error(None, error_msg)
            #                 else:
            #                     if court_type_changed:
            #                         error_msg = self._check_if_time_available(time_str, facility_id, date, court_type, is_only_court_type_changed=True, old_court_type=order.court_type)
            #                         if error_msg:
            #                             form.add_error(None, error_msg)
            #                     else:
            #                         # nothing changed
            #                         pass
            #         if form.non_field_errors():
            #             return HttpResponse(html_template.render({
            #                 "form": form,
            #                 "order_status_selector": order_status_selector,
            #                 "current_order_status": current_order_status,
            #             }, request))

            #         """ === data unfreeze === """
            #         unfreeze(order.facility_id, order.date, util.trans_list_str_to_list(order.time_list), order.court_type)
            #         """ === data freeze === """
            #         freeze(facility_id, date, time_list, court_type)

            # """ === update order === """
            # order.facility_id = facility_id
            # order.phone_number = phone_number
            # order.date = date
            # order.court_type = court_type
            # order.time_list = time_list_str
            # order.status = new_status
            # order.remark = remark
            # order.save()

            return redirect("/dashboard/order/list")

        return HttpResponse(html_template.render({
            "form": form,
            "order_status_selector": order_status_selector,
            "current_order_status": current_order_status,
        }, request))


def check_if_time_available(time_str, facility_id, date, court_type, is_only_court_type_changed = False, old_court_type = None):
    time_obj = datetime.datetime.strptime(time_str, '%H:%M')
    freeze = Freeze.objects.filter(facility_id=facility_id, date=date, time=datetime.time(hour=time_obj.hour, minute=time_obj.minute)).first()
    if freeze:
        new_freeze_weights = freeze.weights - util.get_freeze_weights_by_court_type(old_court_type) + util.get_freeze_weights_by_court_type(court_type) if is_only_court_type_changed else freeze.weights + util.get_freeze_weights_by_court_type(court_type)
        if new_freeze_weights > 1:
            return '{} {} is not available'.format(date, time_str)
        elif freeze.is_lock and freeze.lock_count > 0:
            return '{} {} is locked'.format(date, time_str)
    return None


def get_order_by_order_no(order_no=None):
    if not order_no:
        raise Http404

    order = Order.objects.filter(order_no=order_no).first()
    if not order:
        raise Http404

    return order


@login_required(login_url="/login")
def update_phone_number(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        new_phone_number = json_data.get('new_phone_number', None)
        if new_phone_number == None:
            print("Failed: update_order_phone_number")
            print("Wrong phone number")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong phone number"
            return JsonResponse(resp, safe=False, status=400)
        order.phone_number = new_phone_number
        order.save()
        return JsonResponse(resp, safe=False, status=201)


@login_required(login_url="/login")
def update_facility(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        new_facility_id = json_data.get('new_facility_id', None)
        date = order.date
        court_type = order.court_type
        time_list_str = order.time_list
        time_list = util.trans_list_str_to_list(time_list_str)
        if new_facility_id == None:
            print("Failed: update_order_facility")
            print("Wrong facility")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong facility"
            return JsonResponse(resp, safe=False, status=400)
        if new_facility_id == order.facility_id:
            return JsonResponse(resp, safe=False, status=201)
        # no need freeze if status is Reject
        if order.status == OrderStatus.REJECTED:
            order.facility_id = new_facility_id
            order.save()
            return JsonResponse(resp, safe=False, status=201)
        """ === data check === """
        for time_str in time_list:
            errmsg_list = []
            errmsg = check_if_time_available(time_str, new_facility_id, date, court_type)
            if errmsg:
                errmsg_list.append(errmsg)
        if len(errmsg_list) > 0:
            resp['errcode'] = 1
            resp['errmsg'] = "\n".join(errmsg_list)
            return JsonResponse(resp, safe=False, status=400)
        """ === data unfreeze === """
        unfreeze(order.facility_id, order.date, util.trans_list_str_to_list(order.time_list), order.court_type)
        """ === data freeze === """
        freeze(new_facility_id, date, time_list, court_type)
        order.facility_id = new_facility_id
        order.save()
        return JsonResponse(resp, safe=False, status=201)


@login_required(login_url="/login")
def update_date(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        facility_id = order.facility_id
        new_date = json_data.get('new_date', None)
        court_type = order.court_type
        time_list_str = order.time_list
        time_list = util.trans_list_str_to_list(time_list_str)
        if new_date == None:
            print("Failed: update_order_date")
            print("Wrong date")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong date"
            return JsonResponse(resp, safe=False, status=400)
        if new_date == order.date:
            return JsonResponse(resp, safe=False, status=201)
        # no need freeze if status is Reject
        if order.status == OrderStatus.REJECTED:
            order.date = new_date
            order.save()
            return JsonResponse(resp, safe=False, status=201)
        """ === data check === """
        for time_str in time_list:
            errmsg_list = []
            errmsg = check_if_time_available(time_str, facility_id, new_date, court_type)
            if errmsg:
                errmsg_list.append(errmsg)
        if len(errmsg_list) > 0:
            resp['errcode'] = 1
            resp['errmsg'] = "\n".join(errmsg_list)
            return JsonResponse(resp, safe=False, status=400)
        """ === data unfreeze === """
        unfreeze(order.facility_id, order.date, util.trans_list_str_to_list(order.time_list), order.court_type)
        """ === data freeze === """
        freeze(facility_id, new_date, time_list, court_type)
        order.date = new_date
        order.save()
        return JsonResponse(resp, safe=False, status=201)


@login_required(login_url="/login")
def update_court_type(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        facility_id = order.facility_id
        date = order.date
        new_court_type = json_data.get('new_court_type', None)
        time_list_str = order.time_list
        time_list = util.trans_list_str_to_list(time_list_str)
        if new_court_type == None:
            print("Failed: update_order_court_type")
            print("Wrong court type")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong court type"
            return JsonResponse(resp, safe=False, status=400)
        if new_court_type == order.court_type:
            return JsonResponse(resp, safe=False, status=201)
        # no need freeze if status is Reject
        if order.status == OrderStatus.REJECTED:
            order.court_type = new_court_type
            order.save()
            return JsonResponse(resp, safe=False, status=201)
        """ === data check === """
        for time_str in time_list:
            errmsg_list = []
            errmsg = check_if_time_available(time_str, facility_id, date, new_court_type, is_only_court_type_changed=True, old_court_type=order.court_type)
            if errmsg:
                errmsg_list.append(errmsg)
        if len(errmsg_list) > 0:
            resp['errcode'] = 1
            resp['errmsg'] = "\n".join(errmsg_list)
            return JsonResponse(resp, safe=False, status=400)
        """ === data unfreeze === """
        unfreeze(order.facility_id, order.date, util.trans_list_str_to_list(order.time_list), order.court_type)
        """ === data freeze === """
        freeze(facility_id, date, time_list, new_court_type)
        order.court_type = new_court_type
        order.save()
        return JsonResponse(resp, safe=False, status=201)


@login_required(login_url="/login")
def update_time(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        facility_id = order.facility_id
        date = order.date
        court_type = order.court_type
        new_time_list_str = json_data.get('new_time_list', None)
        new_time_list = util.trans_list_str_to_list(new_time_list_str)
        if new_time_list_str == None:
            print("Failed: update_order_time")
            print("Wrong time")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong time"
            return JsonResponse(resp, safe=False, status=400)
        if new_time_list_str == order.time_list:
            return JsonResponse(resp, safe=False, status=201)
        # no need freeze if status is Reject
        if order.status == OrderStatus.REJECTED:
            order.time_list = new_time_list_str
            order.save()
            return JsonResponse(resp, safe=False, status=201)
        """ === data check === """
        for time_str in new_time_list:
            errmsg_list = []
            errmsg = check_if_time_available(time_str, facility_id, date, court_type)
            if errmsg:
                errmsg_list.append(errmsg)
        if len(errmsg_list) > 0:
            resp['errcode'] = 1
            resp['errmsg'] = "\n".join(errmsg_list)
            return JsonResponse(resp, safe=False, status=400)
        """ === data unfreeze === """
        unfreeze(order.facility_id, order.date, util.trans_list_str_to_list(order.time_list), order.court_type)
        """ === data freeze === """
        freeze(facility_id, date, new_time_list, court_type)
        order.time_list = new_time_list_str
        order.save()
        return JsonResponse(resp, safe=False, status=201)


@login_required(login_url="/login")
def update_status(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        new_status = json_data.get('new_status', None)
        old_status = order.status
        facility_id = order.facility_id
        date = order.date
        court_type = order.court_type
        time_list_str = order.time_list
        time_list = util.trans_list_str_to_list(time_list_str)
        if new_status == None:
            print("Failed: update_order_status")
            print("Wrong new_status")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong new_status"
            return JsonResponse(resp, safe=False, status=400)
        if old_status == new_status:
            return JsonResponse(resp, safe=False, status=201)
        elif old_status == OrderStatus.REJECTED:  # only freeze needed
            """ === data check === """
            for time_str in time_list:
                errmsg_list = []
                errmsg = check_if_time_available(time_str, facility_id, date, court_type)
                if errmsg:
                    errmsg_list.append(errmsg)
            if len(errmsg_list) > 0:
                resp['errcode'] = 1
                resp['errmsg'] = "\n".join(errmsg_list)
                return JsonResponse(resp, safe=False, status=400)
            """ === data freeze === """
            freeze(facility_id, date, time_list, court_type)
            """ === sms ==="""
            if new_status == OrderStatus.ACCEPTED:
                try:
                    # generate url scheme
                    resp = generate_scheme(order.id)
                    url_scheme = resp.get("openlink", "")
                    # send sms
                    send_sms(
                        phone_number_list=[order.phone_number],
                        template_id=settings.TENCENT_CLOUD_SMS_TEMPLATE_ID_ORDER_UPDATED,
                        template_param_list=[
                            "已成功预定",
                            "{}".format(url_scheme),
                            "has been accepted",
                            "{}".format(url_scheme),
                        ]
                    )
                except Exception as e:
                    print("Failed: send_sms")
                    print(e)
                    pass
        elif old_status != OrderStatus.REJECTED and new_status == OrderStatus.REJECTED:  # only unfreeze needed
            """ === data unfreeze === """
            unfreeze(order.facility_id, order.date, util.trans_list_str_to_list(order.time_list), order.court_type)
            """ === refund === """
            bills = Bill.objects.filter(order_id=order.id)
            for bill in bills:
                refund_amount = bill.amount - bill.refunded_amount
                if bill.bill_type == BillType.PAYMENT and refund_amount > Decimal(0):
                    refund_no = util.generate_refund_no(bill.trade_no)
                    refund(bill.trade_no, refund_no, bill.amount, refund_amount)
                    bill.refunded_amount = bill.amount
                    bill.save()
            """ === sms ==="""
            try:
                # generate url scheme
                resp = generate_scheme(order.id)
                url_scheme = resp.get("openlink", "")
                # send sms
                send_sms(
                    phone_number_list=[order.phone_number],
                    template_id=settings.TENCENT_CLOUD_SMS_TEMPLATE_ID_ORDER_UPDATED,
                    template_param_list=[
                        "已被拒绝",
                        "{}".format(url_scheme),
                        "has been rejected",
                        "{}".format(url_scheme),
                    ]
                )
            except Exception as e:
                print("Failed: send_sms")
                print(e)
                pass
        elif old_status != OrderStatus.REJECTED and new_status != OrderStatus.REJECTED:
            order.status = new_status
            order.save()
            return JsonResponse(resp, safe=False, status=201)
        order.status = new_status
        order.save()
        return JsonResponse(resp, safe=False, status=201)


@login_required(login_url="/login")
def update_price(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        new_price = json_data.get('new_price', None)
        if new_price == None:
            print("Failed: update_order_price")
            print("Wrong price")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong price"
            return JsonResponse(resp, safe=False, status=400)
        
        new_price = Decimal(new_price)
        if new_price > order.price:
            order.price = new_price
            order.status = OrderStatus.PENDING_PAYMENT
            order.save()
            try:
                # generate url scheme
                resp = generate_scheme(order.id)
                url_scheme = resp.get("openlink", "")
                # send sms
                send_sms(
                    phone_number_list=[order.phone_number],
                    template_id=settings.TENCENT_CLOUD_SMS_TEMPLATE_ID_ORDER_UPDATED,
                    template_param_list=[
                        "价格发生改变",
                        "{}".format(url_scheme),
                        "price has been updated",
                        "{}".format(url_scheme),
                    ]
                )
            except Exception as e:
                pass
        elif new_price < order.price:
            bills = Bill.objects.filter(order_id=order.id)
            unpay_amount = calc_unpay_amount(order.id, order, bills)
            if unpay_amount >= order.price - new_price:
                order.price = new_price
                if (unpay_amount == Decimal(0)):
                    order.status = OrderStatus.PENDING_CONFIRMATION
                order.save()
            else:
                refund_amount = order.price - new_price + unpay_amount
                for bill in bills:
                    refunded_amount = bill.refunded_amount or Decimal(0)
                    if refund_amount > Decimal(0) and bill.bill_type == BillType.PAYMENT and (bill.amount - refunded_amount > Decimal(0)):
                        available_refund_amount = bill.amount - refunded_amount
                        refund_no = util.generate_refund_no(bill.trade_no)
                        if available_refund_amount >= refund_amount:
                            refund(bill.trade_no, refund_no, bill.amount, refund_amount)
                            bill.refunded_amount = refunded_amount + refund_amount
                            bill.save()
                            refund_amount = Decimal(0)
                        else:
                            refund(bill.trade_no, refund_no, bill.amount, available_refund_amount)
                            bill.refunded_amount = bill.amount
                            bill.save()
                            refund_amount -= available_refund_amount
                order.price = new_price
                order.save()
        return JsonResponse(resp, safe=False, status=201)


@login_required(login_url="/login")
def update_remark(request, order_no=None):
    if request.method == 'POST':
        order = get_order_by_order_no(order_no)

        resp = {"errcode": 0, "errmsg": ""}
        json_data = json.loads(request.body)
        new_remark = json_data.get('new_remark', None)
        if new_remark == None:
            print("Failed: update_order_remark")
            print("Wrong remark")
            resp['errcode'] = 1
            resp['errmsg'] = "Wrong remark"
            return JsonResponse(resp, safe=False, status=400)
        order.remark = new_remark
        order.save()
        return JsonResponse(resp, safe=False, status=201)
