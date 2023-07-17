# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from typing import Any, Dict
from django import template
from django.db.models.query import QuerySet
from django.views import View
from django.views.generic.list import ListView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.template import loader
from django.urls import reverse
from django.core.paginator import Paginator

import json

from apps.dashboard.forms.staduim import StadiumForm
from apps.dashboard.models import Stadium, StadiumImage
from utils.oss import get_upload_file_info, upload_file, get_image_url_by_fiel_path, get_download_url_by_file_id


NUMBER_OF_PAGE = 25


class StadiumListView(LoginRequiredMixin, ListView):
    model = Stadium
    paginate_by = NUMBER_OF_PAGE
    template_name = 'dashboard/stadium.html'

    def get_queryset(self) -> QuerySet[Any]:
        context = Stadium.objects.all()
        return context

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context


class StadiumView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, id=None):
        context = {}
        if not id:
            form = StadiumForm(request.POST or None)
            html_template = loader.get_template('dashboard/stadium-form.html')
            return HttpResponse(html_template.render({"form": form}, request))

        stadium = Stadium.objects.get(id=id)

        form = StadiumForm(request.POST or None, instance=stadium)
        html_template = loader.get_template('dashboard/stadium-form.html')
        return HttpResponse(html_template.render({"form": form}, request))

    def post(self, request, id=None):
        # create
        if not id:
            form = StadiumForm(request.POST or None)
        # update
        else:
            stadium = Stadium.objects.get(id=id)
            form = StadiumForm(request.POST or None, instance=stadium)

        if form.is_valid():
            stadium = form.save()
            return redirect("/dashboard/stadium/list")

        return render(request, "dashboard/stadium-form.html", {"form": form})

    def delete(self, request, id):
        try:
            stadium = Stadium.objects.get(id=id)
            stadium.delete()
        except:
            pass
        return HttpResponse("", status=204)


class StadiumImageView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, id=None):
        json_data = json.loads(request.body)
        file_path = json_data.get('file_path', '')
        file_id = json_data.get('file_id', '')
        stadium = Stadium.objects.filter(id=id).first()
        if stadium:
            StadiumImage.objects.create(stadium=stadium, file_path=file_path, file_id=file_id)
        return JsonResponse({}, safe=False, status=201)


def get_stadium_image_list(request, id=None):
    if request.method == 'GET':
        image_list = StadiumImage.objects.filter(stadium__pk=id)
        result = []
        for image in image_list:
            image_url = get_image_url_by_fiel_path(image.file_path)
            result.append({
                "id": image.id,
                "image_url": image_url,
                "file_id": image.file_id
            })
        return JsonResponse(result, safe=False)


@login_required(login_url="/login")
def delete_stadium_image_by_file_id(request):
    if (request.method == 'DELETE'):
        try:
            json_data = json.loads(request.body)
            file_id = json_data.get('file_id')
            image = StadiumImage.objects.get(file_id=file_id)
            image.delete()
        except:
            pass
        return HttpResponse("", status=204)

