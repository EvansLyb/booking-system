# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.views import View
from django.views.generic.list import ListView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.template import loader
from django.core.paginator import Paginator

import math
import uuid
import requests
import json

from apps.dashboard.models import Facility, FacilityCoverImage
from apps.dashboard.forms.facility import FacilityForm
from utils.oss import get_upload_file_info, upload_file, get_image_url_by_fiel_path, get_download_url_by_file_id


NUMBER_OF_PAGE = 25

class FacilityListView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        context = {'segment': 'facility'}

        facility_list = Facility.objects.all().order_by('id')
        paginator = Paginator(facility_list, NUMBER_OF_PAGE)
        # context - page
        current_page = request.GET.get("page")
        context['current_page'] = current_page
        page_count = math.ceil(paginator.count / NUMBER_OF_PAGE)
        context['page_count'] = page_count
        context['page_range'] = range(1, page_count + 1)
        # context - obj
        page_obj = paginator.get_page(current_page)
        # inject cover image
        for idx, facility in enumerate(page_obj):
            cover_image_list = FacilityCoverImage.objects.filter(facility=facility)
            page_obj[idx].cover_image_list = [get_image_url_by_fiel_path(cover_image.file_path) for cover_image in cover_image_list]
        context['facility_list'] = page_obj

        html_template = loader.get_template('dashboard/facility.html')
        return HttpResponse(html_template.render(context, request))


class FacilityView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, id=None):
        context = {}
        if not id:
            form = FacilityForm(request.POST or None, request.FILES or None)
            html_template = loader.get_template('dashboard/facility-form.html')
            return HttpResponse(html_template.render({"form": form}, request))

        facility = Facility.objects.get(id=id)

        form = FacilityForm(request.POST or None, request.FILES or None, instance=facility)
        html_template = loader.get_template('dashboard/facility-form.html')
        return HttpResponse(html_template.render({"form": form}, request))

    def post(self, request, id=None):
        # create
        if not id:
            form = FacilityForm(request.POST or None, request.FILES or None)
        # update
        else:
            facility = Facility.objects.get(id=id)
            form = FacilityForm(request.POST or None, request.FILES or None, instance=facility)

        if form.is_valid():
            facility = form.save()
            # delete old cover images
            FacilityCoverImage.objects.filter(facility=facility).delete()
            # reset cover images
            cover_image_list = request.FILES.getlist('cover_image_list')
            for image in cover_image_list:
                file_path = "booking-system/{}-{}".format(uuid.uuid4().hex, image.name)
                resp = get_upload_file_info(file_path)
                upload_file(
                    resp.get('url'),
                    file_path,
                    resp.get('authorization'),
                    resp.get('token'),
                    resp.get('cos_file_id'),
                    image
                )
                FacilityCoverImage.objects.create(
                    facility=facility,
                    file_path=file_path,
                    file_id=resp.get("file_id", "")
                )
            return redirect("/dashboard/facility/list")

        return render(request, "dashboard/facility-form.html", {"form": form})

    def delete(self, request, id):
        try:
            facility = Facility.objects.get(id=id)
            facility.delete()
        except:
            pass
        return HttpResponse("", status=204)


def get_cover_image_list(request, fid=None):
    if request.method == 'GET':
        cover_image_list = FacilityCoverImage.objects.filter(facility__pk=fid)
        result = []
        for cover_image in cover_image_list:
            image_url = get_image_url_by_fiel_path(cover_image.file_path)
            result.append({
                "id": cover_image.id,
                "image_url": image_url
            })
        return JsonResponse(result, safe=False)


def download_cover_image_by_url(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        url = json_data.get('url', '')
        resp = requests.get(url=url)
        return FileResponse(resp, as_attachment=False)

# @login_required(login_url="/login")
# def post_cover_image(request, fid=None):
#     if (request.method == 'POST' and fid):
#         cover_image_list = request.FILES.getlist('cover_image_list')
#         facility = Facility.objects.filter(id=fid).first()
#         for image in cover_image_list:
#             FacilityCoverImage.objects.create(facility=facility, image=image)
#         return HttpResponse("", status=201)


# @login_required(login_url="/login")
# def delete_cover_image(request, id=None):
#     if (request.method == 'DELETE'):
#         try:
#             cover_image = FacilityCoverImage.objects.get(id=id)
#             cover_image.delete()
#         except:
#             pass
#         return HttpResponse("", status=204)
