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
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.template import loader
from django.urls import reverse
from django.core.paginator import Paginator

from datetime import datetime, date, time, timedelta
import math

from apps.authentication.models import Account
from .models import Facility, Price, LockInfo, Freeze
from .forms.account import AccountForm
from .forms.facility import FacilityForm
from .forms.price import PriceForm
from .forms.lock import LockForm
from .utils import merge_time_list, split_time, split_time_list


NUMBER_OF_PAGE = 25


class AccountListView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        context = {'segment': 'account'}

        NUMBER_OF_PAGE = 25
        account_list = Account.objects.all()
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


class FacilityListView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        context = {'segment': 'facility'}

        NUMBER_OF_PAGE = 25
        facility_list = Facility.objects.all()
        paginator = Paginator(facility_list, NUMBER_OF_PAGE)
        # context - page
        current_page = request.GET.get("page")
        context['current_page'] = current_page
        page_count = math.ceil(paginator.count / NUMBER_OF_PAGE)
        context['page_count'] = page_count
        context['page_range'] = range(1, page_count + 1)
        # context - obj
        page_obj = paginator.get_page(current_page)
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
        # cover image
        cover_image = facility.cover_image

        form = FacilityForm(request.POST or None, request.FILES or None, instance=facility)
        html_template = loader.get_template('dashboard/facility-form.html')
        return HttpResponse(html_template.render({"form": form, "cover_image": cover_image}, request))

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
            low_time_price = form.cleaned_data['low_time_price']
            high_time_price = form.cleaned_data['high_time_price']
            separation_timing = form.cleaned_data['separation_timing']
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
                price.low_time_price = clean_price(low_time_price)
                price.high_time_price = clean_price(high_time_price)
                price.separation_timing = separation_timing
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
                    low_time_price=clean_price(low_time_price),
                    high_time_price=clean_price(high_time_price),
                    separation_timing=separation_timing
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


class LockView(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, fid=None):
        if not fid:
            return HttpResponseRedirect('404', status=404)

        form = LockForm(request.POST or None)
        html_template = loader.get_template('dashboard/facility-lock-form.html')
        return HttpResponse(html_template.render({"form": form}, request))

    def post(self, request, fid=None):
        form = LockForm(request.POST or None)
        act = request.GET.get("act")
        if form.is_valid() and act == 'lock':
            date = form.cleaned_data['date']
            from_time = form.cleaned_data['from_time']
            to_time = form.cleaned_data['to_time']
            from_time_str = from_time.isoformat(timespec='minutes')
            to_time_str = to_time.isoformat(timespec='minutes')
            delta = timedelta(minutes=30)
            d = datetime.strptime(from_time_str, '%H:%M')
            while d < datetime.strptime(to_time_str, '%H:%M'):
                Freeze.objects.update_or_create(
                    facility_id=fid,
                    date=date,
                    time=d,
                    defaults={
                        'facility_id': fid,
                        'date': date,
                        'is_lock': True,
                        'time': time(hour=d.hour, minute=d.minute)
                    }
                )
                d += delta
            # merge lock info
            lock_info = LockInfo.objects.filter(facility_id=fid, date=date).first()
            if lock_info:
                slot_list = lock_info.slot.split(', ')
                slot_list.append("{}-{}".format(from_time_str, to_time_str))  # append the new slot
                merged_slot_list = merge_time_list(slot_list)  # merge slot
                lock_info.slot = ', '.join(merged_slot_list)
            else:
                lock_info = LockInfo(
                    facility_id=fid,
                    date=date,
                    slot="{}-{}".format(from_time_str, to_time_str)
                )
            lock_info.save()
            return redirect("/dashboard/facility/list")
        print(form.errors)
        if form.is_valid() and act == 'unlock':
            date = form.cleaned_data['date']
            from_time = form.cleaned_data['from_time']
            to_time = form.cleaned_data['to_time']
            from_time_str = from_time.isoformat(timespec='minutes')
            to_time_str = to_time.isoformat(timespec='minutes')
            delta = timedelta(minutes=30)
            d = datetime.strptime(from_time_str, '%H:%M')
            while d < datetime.strptime(to_time_str, '%H:%M'):
                freeze = Freeze.objects.filter(
                    facility_id=fid,
                    date=date,
                    time=d,
                    is_lock=True
                ).first()
                if freeze:
                    if freeze.is_order:
                        freeze.is_lock = False
                        freeze.save()
                    else:
                        freeze.delete()
                d += delta
            # split lock info
            lock_info = LockInfo.objects.filter(facility_id=fid, date=date).first()
            if lock_info:
                slot_list = lock_info.slot.split(', ')
                splited_slot_list = split_time_list(slot_list, "{}-{}".format(from_time_str, to_time_str))  # split slot
                if len(splited_slot_list) == 0:
                    lock_info.delete()
                else:
                    lock_info.slot = ', '.join(splited_slot_list)
                    lock_info.save()
            return redirect("/dashboard/facility/list")
        return render(request, "dashboard/facility-lock-form.html", {"form": form})


@login_required(login_url="/login")
def get_lock_info(request, fid=None):
    if request.method == 'GET':
        today = date.today()
        lock_info_list = LockInfo.objects.filter(
            facility_id=fid,
            date__gte=today,
        ).order_by('date')
        serialized_data = serialize("json", lock_info_list)
        return JsonResponse(serialized_data, safe=False)



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
