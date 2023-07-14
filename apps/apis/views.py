# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.db import transaction
from django.conf import settings

import json
import requests
import datetime
import ast
from decimal import Decimal

from apps.dashboard.models import Facility, Stadium, FacilityCoverImage, Price, Freeze, Order, Bill, OrderStatus, BillType
from apps.apis.models import User
from utils.payment import unified_order
from utils.sms import send_sms
from utils.util import get_freeze_weights_by_court_type, generate_order_no, generate_trade_no, get_order_no_by_trade_no
from utils.order import calc_unpay_amount, freeze, unfreeze


def get_facility_list(request):
    if request.method == 'GET':
        resp = []
        facility_list = Facility.objects.all()
        for facility in facility_list:
            cover_image_list = FacilityCoverImage.objects.filter(facility=facility).order_by('id')
            content = {
                "id": facility.pk,
                "name": facility.name,
                "cover_image_list": [cover_image.file_id for cover_image in cover_image_list],
                "description": facility.description
            }
            resp.append(content)

        return JsonResponse(resp, safe=False)


def get_stadium_list(request):
    if request.method == 'GET':
        stadium_list = Stadium.objects.all()
        resp = []
        for stadium in stadium_list:
            resp.append({
                "name": stadium.name,
                "longitude": stadium.longitude,
                "latitude": stadium.latitude,
                "location": stadium.location,
                "description": stadium.description
            })
        return JsonResponse(resp, safe=False)


def bind_phone_number(request):
    if request.method == 'POST':
        open_id = request.headers.get('X-Wx-Openid', '')
        if not open_id:
            return JsonResponse({}, safe=False, status=400)

        json_data = json.loads(request.body)
        code = json_data.get('code', None)
        if not code:
            return JsonResponse({}, safe=False, status=400)

        # fetch phone number by code
        request_url = "http://api.weixin.qq.com/wxa/business/getuserphonenumber"
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        data = {
            "code": code
        }
        try:
            resp = requests.post(request_url, json=data, headers=headers)
            resp = resp.json()
            phone_number = resp.get('phone_info', {}).get('phoneNumber')
            User.objects.get_or_create(
                open_id=open_id,
                phone_number=phone_number
            )
        except Exception as e:
            print(e)
            raise e

        return JsonResponse({
            "phone_number": phone_number
        }, safe=False, status=201)


def check_phone_number(request):
    if request.method == 'GET':
        open_id = request.headers.get('X-Wx-Openid', '')
        if not open_id:
            return JsonResponse({}, safe=False, status=400)
        user = User.objects.filter(open_id=open_id).first()
        if not user:
            return JsonResponse({
                "phone_numer": "",
                "is_bound": False
            }, safe=False, status=200)

        return JsonResponse({
            "phone_numer": user.phone_number,
            "is_bound": True
        }, safe=False, status=200)


def get_price_info(request, fid=None):
    if request.method == 'GET':
        resp = {}
        if not fid:
            resp['price_list'] = []
            return JsonResponse(resp, safe=False)

        price_list = []
        price_obj_list = Price.objects.filter(facility_id=fid)
        for price_obj in price_obj_list:
            price_list.append({
                "court_type": price_obj.court_type,
                "day_type": price_obj.day_type,
                "opening_time": price_obj.opening_time,
                "closing_time": price_obj.closing_time,
                "full_day_price": price_obj.full_day_price,
                "normal_hourly_price": price_obj.normal_hourly_price,
                "peek_hourly_price": price_obj.peek_hourly_price,
                "peek_time_from": price_obj.peek_time_from,
                "peek_time_to": price_obj.peek_time_to
            })
        resp['price_list'] = price_list
        return JsonResponse(resp, safe=False)


def get_freeze(request):
    if request.method == 'GET':
        resp = []
        fid = request.GET.get('fid')
        date = request.GET.get('date')
        if not fid or not date:
            return JsonResponse(resp, safe=False)
        freeze_list = Freeze.objects.filter(
            facility_id=int(fid),
            date=date,
            lock_count__gt=0
        ) | Freeze.objects.filter(
            facility_id=int(fid),
            date=date,
            is_order=True,
            weights__gt=0
        )
        for freeze in freeze_list:
            resp.append({
                "facility_id": int(fid),
                "date": date,
                "weights": freeze.weights,
                "is_lock": freeze.is_lock,
                "time": freeze.time
            })
        return JsonResponse(resp, safe=False)


@transaction.atomic
def create_order(request):
    def _freeze(facility_id, date, time_list, court_type):
        # data check
        for time_str in time_list:
            time_obj = datetime.datetime.strptime(time_str, '%H:%M')
            freeze = Freeze.objects.filter(facility_id=facility_id, date=date, time=datetime.time(hour=time_obj.hour, minute=time_obj.minute)).first()
            if freeze:
                new_freeze_weights = freeze.weights + get_freeze_weights_by_court_type(court_type)
                if new_freeze_weights > 1:
                    raise Exception('Already sold out. facility_id={}, date={}, time={}, court_type={}'.format(facility_id, date, time_str, court_type))
                if freeze.is_lock and freeze.lock_count > 0:
                    raise Exception('Locked')
        # freeze
        for time_str in time_list:
            time_obj = datetime.datetime.strptime(time_str, '%H:%M')
            freeze = Freeze.objects.filter(facility_id=facility_id, date=date, time=datetime.time(hour=time_obj.hour, minute=time_obj.minute)).first()
            if freeze:
                freeze.is_order = True
                freeze.weights = freeze.weights + get_freeze_weights_by_court_type(court_type)
            else:
                freeze = Freeze(
                    facility_id=facility_id,
                    date=date,
                    time=datetime.time(hour=time_obj.hour, minute=time_obj.minute),
                    is_order=True,
                    weights=get_freeze_weights_by_court_type(court_type)
                )
            freeze.save()

    if request.method == 'POST':
        open_id = request.headers.get('X-Wx-Openid', '')
        if not open_id:
            return JsonResponse({"errcode": 1, "errmsg": ""}, safe=False, status=400)

        user = User.objects.filter(open_id=open_id).first()
        if not user:
            print('User does not exist, open_id: {}'.format(open_id))
            return JsonResponse({"errcode": 1, "errmsg": ""}, safe=False, status=400)

        json_data = json.loads(request.body)
        total_price = json_data.get('total_price', None)
        facility_id = json_data.get('facility_id', None)
        date = json_data.get('date', None)
        court_type = json_data.get('court_type', None)
        time_list = json_data.get('time_list', [])
        is_full_day = json_data.get('is_full_day', False)
        remark = json_data.get('remark', '')
        if not total_price or not facility_id or not date or not court_type or len(time_list) == 0:
            return JsonResponse({"errcode": 1, "errmsg": ""}, safe=False, status=400)

        try:
            _freeze(facility_id, date, time_list, court_type)
        except Exception as e:
            print("Failed: create_order")
            print(e)
            return JsonResponse({"errcode": 1, "errmsg": str(e)}, safe=False, status=400)

        if total_price == 0:
            order = Order.objects.create(
                order_no=generate_order_no(),
                facility_id=facility_id,
                user_id=user.id,
                phone_number=user.phone_number,
                status=OrderStatus.PENDING_CONFIRMATION,
                date=datetime.datetime.strptime(date, '%Y-%m-%d'),
                court_type=court_type,
                price=total_price,
                time_list=time_list,
                is_full_day=is_full_day,
                remark=remark
            )
            return JsonResponse({"errcode": 0, "errmsg": "", "order_id": order.id}, safe=False, status=201)
        else:
            order = Order.objects.create(
                order_no=generate_order_no(),
                facility_id=facility_id,
                user_id=user.id,
                phone_number=user.phone_number,
                status=OrderStatus.PENDING_PAYMENT,
                date=datetime.datetime.strptime(date, '%Y-%m-%d'),
                court_type=court_type,
                price=total_price,
                time_list=time_list,
                is_full_day=is_full_day,
                remark=remark
            )
            return JsonResponse({"errcode": 0, "errmsg": "", "order_id": order.id}, safe=False, status=201)


def checkout(request):
    if request.method == 'POST':
        open_id = request.headers.get('X-Wx-Openid', '')
        if not open_id:
            return JsonResponse({"errcode": 1, "errmsg": ""}, safe=False, status=400)

        json_data = json.loads(request.body)
        order_id = json_data.get('order_id', None)
        if order_id == None:
            print("Failed: checkout")
            print("Missing Order ID")
            return JsonResponse({"errcode": 1, "errmsg": "Missing Order ID"}, safe=False, status=400)

        order = Order.objects.filter(id=order_id).first()
        if not order:
            print("Failed: checkout")
            print("Invalid Order ID")
            return JsonResponse({"errcode": 1, "errmsg": "Invalid Order ID"}, safe=False, status=400)

        trade_no = generate_trade_no(order.order_no)
        total_price = calc_unpay_amount(order_id, order)
        ip = request.headers.get('X-Original-Forwarded-For', '127.0.0.1')
        resp = unified_order(open_id=open_id, trade_no=trade_no, total_price=total_price, ip=ip)
        resp_data = resp.get('respdata', {})
        payment_data = resp_data.get('payment', {})
        payment_data["errcode"] = 0
        payment_data["errmsg"] = ""
        return JsonResponse(payment_data, safe=False, status=201)


def payment_callback(request):
    json_data = json.loads(request.body)
    print("payment_callback:")
    print(json_data)
    transaction_id = json_data.get("transactionId", None)
    trade_no = json_data.get("outTradeNo", None)
    price = json_data.get("totalFee", None)
    nonce_str = json_data.get("nonceStr", None)
    if transaction_id == None or trade_no == None or price == None or nonce_str == None:
        return JsonResponse({
            "errcode": 1,
            "errmsg": ""
        }, safe=False, status=400)

    order_no = get_order_no_by_trade_no(trade_no)
    order = Order.objects.filter(order_no=order_no).first()
    order.status = OrderStatus.PENDING_CONFIRMATION
    order.save()

    amount = Decimal(price) / 100
    Bill.objects.create(
        order_id=order.id,
        bill_type=BillType.PAYMENT,
        amount=amount,
        trade_no=trade_no,
        nonce_str=nonce_str,
        transaction_id=transaction_id
    )

    return JsonResponse({
        "errcode": 0,
        "errmsg": ""
    }, safe=False, status=200)


def refund_callback(request):
    json_data = json.loads(request.body)
    print("refund_callback:")
    print(json_data)
    transaction_id = json_data.get("transactionId", None)
    trade_no = json_data.get("outTradeNo", None)
    price = json_data.get("refundFee", None)
    nonce_str = json_data.get("nonceStr", None)
    if transaction_id == None or trade_no == None or price == None or nonce_str == None:
        return JsonResponse({
            "errcode": 1,
            "errmsg": ""
        }, safe=False, status=400)

    refunded_amount = Decimal(price) / 100
    # Create Refund Bill
    order_no = get_order_no_by_trade_no(trade_no)
    order = Order.objects.filter(order_no=order_no).first()
    Bill.objects.create(
        order_id=order.id,
        bill_type=BillType.REFUND,
        amount=refunded_amount,
        trade_no=trade_no,
        nonce_str=nonce_str,
        transaction_id=transaction_id
    )

    return JsonResponse({
        "errcode": 0,
        "errmsg": ""
    }, safe=False, status=200)


def get_order_list(request):
    if request.method == 'GET':
        open_id = request.headers.get('X-Wx-Openid', '')
        if not open_id:
            return JsonResponse({"errcode": 1, "errmsg": "", list: []}, safe=False, status=400)

        user = User.objects.filter(open_id=open_id).first()
        if not user:
            print('User does not exist, open_id: {}'.format(open_id))
            return JsonResponse({"errcode": 1, "errmsg": "", list: []}, safe=False, status=400)

        order_list = Order.objects.filter(user_id=user.id).order_by("-updated_at")
        resp = {
            "errcode": 0,
            "errmsg": "",
            "list": []
        }
        for order in order_list:
            facility_id = order.facility_id
            facility = Facility.objects.filter(id=facility_id).first()
            resp['list'].append({
                "id": order.id,
                "order_no": order.order_no,
                "facility_name": facility.name,
                "status": order.status,
                "date": order.date,
                "court_type": order.court_type,
                "price": order.price,
                "time_list": ast.literal_eval(order.time_list)
            })
        return JsonResponse(resp, safe=False, status=200)


def get_order_details(request, oid=None):
    if request.method == 'GET':
        resp = {
            "errcode": 0,
            "errmsg": ""
        }

        if not oid:
            resp["errcode"] = 1
            return JsonResponse(resp, safe=False, status=400)

        order = Order.objects.filter(id=oid).first()
        if not order:
            resp["errcode"] = 1
            return JsonResponse(resp, safe=False, status=404)

        facility_id = order.facility_id
        facility = Facility.objects.filter(id=facility_id).first()
        cover_image_obj = FacilityCoverImage.objects.filter(facility=facility).first()
        resp["facility_name"] = facility.name
        resp["facility_image"] = cover_image_obj.file_id

        stadium = Stadium.objects.all().first()
        resp["stadium_location"] = stadium.location
        resp["stadium_latitude"] = stadium.latitude
        resp["stadium_longitude"] = stadium.longitude

        resp["order_no"] = order.order_no
        resp["phone_number"] = order.phone_number
        resp["status"] = order.status
        resp["date"] = order.date
        resp["court_type"] = order.court_type
        resp["price"] = order.price
        resp["checkout_price"] = calc_unpay_amount(oid, order)
        resp["created_at"] = order.created_at
        resp["updated_at"] = order.updated_at
        resp["remark"] = order.remark
        resp["time_list"] = ast.literal_eval(order.time_list)
        return JsonResponse(resp, safe=False, status=200)


def t_send_sms(request):
    try:
      resp = send_sms()
      return JsonResponse(resp, safe=False, status=201)
    except Exception as e:
        print("Failed: send_sms")
        print(e)
        raise e
