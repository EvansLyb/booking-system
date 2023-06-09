# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize

from apps.dashboard.models import Facility, Stadium, FacilityCoverImage


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
