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

from datetime import datetime, date, time, timedelta
import math

from apps.authentication.models import Account
from .models import Stadium, Facility, Price, LockInfo, Freeze, FacilityCoverImage
from .forms.account import AccountForm
from .forms.facility import FacilityForm
from .forms.price import PriceForm
from .forms.lock import LockForm
from .forms.staduim import StadiumForm
from .utils import merge_time_list, split_time, split_time_list, daterange


NUMBER_OF_PAGE = 25


class AccountListView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        context = {'segment': 'account'}

        account_list = Account.objects.all().order_by('id')
        paginator = Paginator(account_list, NUMBER_OF_PAGE)
        # context - page
        current_page = request.GET.get("page")
        context['current_page'] = current_page
        page_count = math.ceil(paginator.count / NUMBER_OF_PAGE)
        context['page_count'] = page_count
        context['page_range'] = range(1, page_count + 1)
        # context - obj
        page_obj = paginator.get_page(current_page)
        context['account_list'] = page_obj

        html_template = loader.get_template('dashboard/account.html')
        return HttpResponse(html_template.render(context, request))
    

class AccountView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, id=None):
        context = {}
        if not id:
            form = AccountForm(request.POST or None)
            html_template = loader.get_template('dashboard/account-form.html')
            return HttpResponse(html_template.render({"form": form}, request))

        account = Account.objects.get(id=id)
        form = AccountForm(request.POST or None, instance=account)
        html_template = loader.get_template('dashboard/account-form.html')
        return HttpResponse(html_template.render({"form": form}, request))

    def post(self, request, id=None):
        # create
        if not id:
            form = AccountForm(request.POST or None)
        # update
        else:
            account = Account.objects.get(id=id)
            form = AccountForm(request.POST or None, instance=account)

        if form.is_valid():
            account = form.save()
            return redirect("/dashboard/account/list")

        return render(request, "dashboard/account-form.html", {"form": form})

    def delete(self, request, id):
        try:
            account = Account.objects.get(id=id)
            account.delete()
        except:
            pass
        return HttpResponse("", status=204)


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
            page_obj[idx].cover_image_list = [cover_image.image for cover_image in cover_image_list]
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
                FacilityCoverImage.objects.create(facility=facility, image=image)
            return redirect("/dashboard/facility/list")

        return render(request, "dashboard/facility-form.html", {"form": form})

    def delete(self, request, id):
        try:
            facility = Facility.objects.get(id=id)
            facility.delete()
        except:
            pass
        return HttpResponse("", status=204)



class PriceListView(LoginRequiredMixin, ListView):
    model = Price
    paginate_by = NUMBER_OF_PAGE
    template_name = 'dashboard/price.html'

    def get_queryset(self) -> QuerySet[Any]:
        fid = self.kwargs['fid']
        if (fid == None):
            return super().get_queryset()

        context = Price.objects.filter(facility_id=fid).order_by('id')
        return context

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context


class PriceView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, fid=None, pid=None):
        context = {}
        if not fid:
            return HttpResponseRedirect('404', status=404)
        if not pid:
            form = PriceForm(request.POST or None)
            html_template = loader.get_template('dashboard/price-form.html')
            return HttpResponse(html_template.render({"form": form, "fid": fid}, request))

        price = Price.objects.get(facility_id=fid, id=pid)
        form = PriceForm(request.POST or None, instance=price)
        html_template = loader.get_template('dashboard/price-form.html')
        return HttpResponse(html_template.render({"form": form, "fid": fid}, request))

    def post(self, request, fid=None, pid=None):
        price = None
        if not fid:
            return HttpResponseRedirect('404', status=404)
        # create
        if not pid:
            form = PriceForm(request.POST or None)
        # update
        else:
            price = Price.objects.get(facility_id=fid, id=pid)
            form = PriceForm(request.POST or None)

        if form.is_valid():
            court_type = form.cleaned_data['court_type']
            day_type = form.cleaned_data['day_type']
            opening_time = form.cleaned_data['opening_time']
            closing_time = form.cleaned_data['closing_time']
            full_day_price = form.cleaned_data['full_day_price']
            normal_hourly_price = form.cleaned_data['normal_hourly_price']
            peek_hourly_price = form.cleaned_data['peek_hourly_price']
            peek_time_from = form.cleaned_data['peek_time_from']
            peek_time_to = form.cleaned_data['peek_time_to']
            # reset peek_hourly_price
            if not peek_time_from and not peek_time_to and peek_hourly_price == None:
                peek_hourly_price = normal_hourly_price
            if price:
                # if is another type
                if (price.court_type != court_type or price.day_type != day_type):
                    is_already_set = Price.objects.filter(
                        facility_id=fid,
                        court_type=court_type,
                        day_type=day_type
                    ).count() > 0
                    if is_already_set:
                        form.add_error(field=None, error='This type is already set.')
                        return render(request, "dashboard/price-form.html", {"form": form, "fid": fid})
                price.court_type = court_type
                price.day_type = day_type
                price.opening_time = opening_time
                price.closing_time = closing_time
                price.full_day_price = clean_price(full_day_price)
                price.normal_hourly_price = clean_price(normal_hourly_price)
                price.peek_hourly_price = clean_price(peek_hourly_price)
                price.peek_time_from = peek_time_from
                price.peek_time_to = peek_time_to
            else:
                is_already_set = Price.objects.filter(
                    facility_id=fid,
                    court_type=court_type,
                    day_type=day_type
                ).count() > 0
                if is_already_set:
                    form.add_error(field=None, error='This type is already set.')
                    return render(request, "dashboard/price-form.html", {"form": form, "fid": fid})
                price = Price(
                    facility_id=fid,
                    court_type=court_type,
                    day_type=day_type,
                    opening_time=opening_time,
                    closing_time=closing_time,
                    full_day_price=clean_price(full_day_price),
                    normal_hourly_price=clean_price(normal_hourly_price),
                    peek_hourly_price=clean_price(peek_hourly_price),
                    peek_time_from=peek_time_from,
                    peek_time_to=peek_time_to
                )
            price.save()
            return redirect("/dashboard/facility/{}/price/list".format(fid))

        return render(request, "dashboard/price-form.html", {"form": form, "fid": fid})

    def delete(self, request, fid=None, pid=None):
        try:
            price = Price.objects.get(facility_id=fid, id=pid)
            price.delete()
        except:
            pass
        return HttpResponse("", status=204)


# class LockView(LoginRequiredMixin, View):
#     login_url = '/login'
#     redirect_field_name = 'redirect_to'

#     def get(self, request, fid=None):
#         if not fid:
#             return HttpResponseRedirect('404', status=404)

#         form = LockForm(request.POST or None)
#         html_template = loader.get_template('dashboard/facility-lock-form.html')
#         return HttpResponse(html_template.render({"form": form}, request))

#     def post(self, request, fid=None):
#         form = LockForm(request.POST or None)
#         act = request.GET.get("act")
#         if form.is_valid() and act == 'lock':
#             from_date = form.cleaned_data['from_date']
#             to_date = form.cleaned_data['to_date']
#             from_time = form.cleaned_data['from_time']
#             to_time = form.cleaned_data['to_time']
#             from_time_str = from_time.isoformat(timespec='minutes')
#             to_time_str = to_time.isoformat(timespec='minutes')
#             delta = timedelta(minutes=30)

#             for single_date in daterange(from_date, to_date):
#                 d = datetime.strptime(from_time_str, '%H:%M')
#                 while d < datetime.strptime(to_time_str, '%H:%M'):
#                     freeze = Freeze.objects.filter(facility_id=fid, date=single_date, time=time(hour=d.hour, minute=d.minute)).first()
#                     if freeze:
#                         freeze.lock_count = freeze.lock_count + 1
#                         freeze.is_lock = True
#                     else:
#                         freeze = Freeze(
#                             facility_id=fid,
#                             date=single_date,
#                             time=time(hour=d.hour, minute=d.minute),
#                             is_lock=True,
#                             lock_count=1
#                         )
#                     freeze.save()
#                     d += delta

#             # Lock Info Model
#             lock_info = LockInfo(
#                 facility_id=fid,
#                 from_date=from_date,
#                 to_date=to_date,
#                 slot="{}-{}".format(from_time_str, to_time_str),
#                 operator=request.user.username  # set operator
#             )
#             lock_info.save()
#             return redirect("/dashboard/facility/list")
        
#         """
#         ================
#          - deprecated
#         ================
#         """
#         if form.is_valid() and act == 'unlock':
#             date = form.cleaned_data['date']
#             from_time = form.cleaned_data['from_time']
#             to_time = form.cleaned_data['to_time']
#             from_time_str = from_time.isoformat(timespec='minutes')
#             to_time_str = to_time.isoformat(timespec='minutes')
#             delta = timedelta(minutes=30)
#             d = datetime.strptime(from_time_str, '%H:%M')
#             while d < datetime.strptime(to_time_str, '%H:%M'):
#                 freeze = Freeze.objects.filter(
#                     facility_id=fid,
#                     date=date,
#                     time=d,
#                     is_lock=True
#                 ).first()
#                 if freeze:
#                     if freeze.is_order:
#                         freeze.is_lock = False
#                         freeze.save()
#                     else:
#                         freeze.delete()
#                 d += delta
#             # split lock info
#             lock_info = LockInfo.objects.filter(facility_id=fid, date=date).first()
#             if lock_info:
#                 slot_list = lock_info.slot.split(', ')
#                 splited_slot_list = split_time_list(slot_list, "{}-{}".format(from_time_str, to_time_str))  # split slot
#                 if len(splited_slot_list) == 0:
#                     lock_info.delete()
#                 else:
#                     lock_info.slot = ', '.join(splited_slot_list)
#                     lock_info.save()
#             return redirect("/dashboard/facility/list")
#         return render(request, "dashboard/facility-lock-form.html", {"form": form})
    
#     def delete(self, request, fid=None, lid=None):
#         lock_info = LockInfo.objects.filter(id=lid).first()
#         from_date = lock_info.from_date
#         to_date = lock_info.to_date
#         slot = lock_info.slot
#         from_time_str, to_time_str = split_time(slot)
#         delta = timedelta(minutes=30)
#         for single_date in daterange(from_date, to_date):
#             d = datetime.strptime(from_time_str, '%H:%M')
#             while d < datetime.strptime(to_time_str, '%H:%M'):
#                 freeze = Freeze.objects.filter(facility_id=fid, date=single_date, time=time(hour=d.hour, minute=d.minute)).first()
#                 if freeze:
#                     freeze.lock_count = freeze.lock_count - 1
#                     if freeze.lock_count <= 0:
#                         if freeze.is_order:
#                             freeze.is_lock = False
#                             freeze.save()
#                         else:
#                             freeze.delete()
#                     else:
#                         freeze.save()
#                 d += delta

#         # Delete Lock Info
#         lock_info = LockInfo.objects.filter(id=lid).first()
#         lock_info.delete()

#         return HttpResponse("", status=204)


# @login_required(login_url="/login")
# def get_lock_info(request, fid=None):
#     if request.method == 'GET':
#         today = date.today()
#         lock_info_obj_list = LockInfo.objects.filter(
#             facility_id=fid,
#             to_date__gte=today,
#         ).order_by('to_date')
#         resp = {}
#         lock_info_list = []
#         for lock_info in lock_info_obj_list:
#             lock_info_list.append({
#                 "id": lock_info.pk,
#                 "from_date": lock_info.from_date,
#                 "to_date": lock_info.to_date,
#                 "slot": lock_info.slot,
#                 "operator": lock_info.operator,
#                 "lock_type": lock_info.lock_type
#             })
#         resp['lock_info_list'] = lock_info_list
#         resp['current_login_user'] = {
#             "username": request.user.username,
#             "is_super_admin": request.user.is_super_admin
#         }
#         return JsonResponse(resp, safe=False)


def get_cover_image_list(request, fid=None):
    if request.method == 'GET':
        cover_image_list = FacilityCoverImage.objects.filter(facility__pk=fid)
        result = []
        for cover_image in cover_image_list:
            result.append({
                "id": cover_image.id,
                "image": cover_image.image.url
            })
        return JsonResponse(result, safe=False)


@login_required(login_url="/login")
def post_cover_image(request, fid=None):
    if (request.method == 'POST' and fid):
        cover_image_list = request.FILES.getlist('cover_image_list')
        facility = Facility.objects.filter(id=fid).first()
        for image in cover_image_list:
            FacilityCoverImage.objects.create(facility=facility, image=image)
        return HttpResponse("", status=201)


@login_required(login_url="/login")
def delete_cover_image(request, id=None):
    if (request.method == 'DELETE'):
        try:
            cover_image = FacilityCoverImage.objects.get(id=id)
            cover_image.delete()
        except:
            pass
        return HttpResponse("", status=204)


@login_required(login_url="/login")
def pages(request):
    context = {}

    template = get_template(request)
    context['segment'] = template

    html_template = loader.get_template('dashboard/' + template)
    return HttpResponse(html_template.render(context, request))


def get_template(request):
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        return load_template

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('dashboard/page-404.html')
        return HttpResponse(html_template.render({}, request))

    except:
        html_template = loader.get_template('dashboard/page-500.html')
        return HttpResponse(html_template.render({}, request))


def clean_price(decimal_price):
    return decimal_price
