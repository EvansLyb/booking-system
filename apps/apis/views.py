# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize

import json
import requests

from apps.dashboard.models import Facility, Stadium, FacilityCoverImage
from apps.apis.models import User


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
