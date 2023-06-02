# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize

from apps.dashboard.models import Facility


def get_facility_list(request):

    if request.method == 'GET':
        facility_list = Facility.objects.all()
        serialized_data = serialize("json", facility_list)
        return JsonResponse(serialized_data, safe=False)
