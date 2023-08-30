# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader

from datetime import datetime, date, time, timedelta

from apps.dashboard.models import LockInfo, Freeze, LockType
from apps.dashboard.forms.lock import LockForm
from apps.dashboard.utils import merge_time_list, split_time, split_time_list, daterange


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
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            from_time = form.cleaned_data['from_time']
            to_time = form.cleaned_data['to_time']
            lock_type = form.cleaned_data['lock_type']
            from_time_str = from_time.isoformat(timespec='minutes')
            to_time_str = to_time.isoformat(timespec='minutes')
            delta = timedelta(minutes=30)

            for single_date in daterange(from_date, to_date):
                # --- LockType.REPEAT ---
                if lock_type == LockType.REPEAT_MONDAY and single_date.weekday() != 0:
                    continue
                elif lock_type == LockType.REPEAT_TUESDAY and single_date.weekday() != 1:
                    continue
                elif lock_type == LockType.REPEAT_WEDNESDAY and single_date.weekday() != 2:
                    continue
                elif lock_type == LockType.REPEAT_THURSDAY and single_date.weekday() != 3:
                    continue
                elif lock_type == LockType.REPEAT_FRIDAY and single_date.weekday() != 4:
                    continue
                elif lock_type == LockType.REPEAT_SATURDAY and single_date.weekday() != 5:
                    continue
                elif lock_type == LockType.REPEAT_SUNDAY and single_date.weekday() != 6:
                    continue
                d = datetime.strptime(from_time_str, '%H:%M')
                end = datetime.strptime(to_time_str, '%H:%M')
                # --- LockType.CONTINUOUS
                if lock_type == LockType.CONTINUOUS:
                    d = datetime.strptime(from_time_str, '%H:%M') if single_date == from_date else datetime.strptime("00:00", '%H:%M')
                    end = datetime.strptime(to_time_str, '%H:%M') if single_date == to_date else datetime.strptime("23:59", '%H:%M')
                while d < end:
                    freeze = Freeze.objects.filter(facility_id=fid, date=single_date, time=time(hour=d.hour, minute=d.minute)).first()
                    if freeze:
                        freeze.lock_count = freeze.lock_count + 1
                        freeze.is_lock = True
                    else:
                        freeze = Freeze(
                            facility_id=fid,
                            date=single_date,
                            time=time(hour=d.hour, minute=d.minute),
                            is_lock=True,
                            lock_count=1
                        )
                    freeze.save()
                    d += delta

            # Lock Info Model
            lock_info = LockInfo(
                facility_id=fid,
                from_date=from_date,
                to_date=to_date,
                slot="{}-{}".format(from_time_str, to_time_str),
                lock_type=lock_type,
                operator=request.user.username  # set operator
            )
            lock_info.save()
            return redirect("/dashboard/facility/list")
        
        return render(request, "dashboard/facility-lock-form.html", {"form": form})
    
    def delete(self, request, fid=None, lid=None):
        lock_info = LockInfo.objects.filter(id=lid).first()
        from_date = lock_info.from_date
        to_date = lock_info.to_date
        lock_type = lock_info.lock_type
        slot = lock_info.slot
        from_time_str, to_time_str = split_time(slot)
        delta = timedelta(minutes=30)
        for single_date in daterange(from_date, to_date):
            # --- LockType.REPEAT ---
            if lock_type == LockType.REPEAT_MONDAY and single_date.weekday() != 0:
                continue
            elif lock_type == LockType.REPEAT_TUESDAY and single_date.weekday() != 1:
                continue
            elif lock_type == LockType.REPEAT_WEDNESDAY and single_date.weekday() != 2:
                continue
            elif lock_type == LockType.REPEAT_THURSDAY and single_date.weekday() != 3:
                continue
            elif lock_type == LockType.REPEAT_FRIDAY and single_date.weekday() != 4:
                continue
            elif lock_type == LockType.REPEAT_SATURDAY and single_date.weekday() != 5:
                continue
            elif lock_type == LockType.REPEAT_SUNDAY and single_date.weekday() != 6:
                continue
            d = datetime.strptime(from_time_str, '%H:%M')
            end = datetime.strptime(to_time_str, '%H:%M')
            # --- LockType.CONTINUOUS
            if lock_type == LockType.CONTINUOUS:
                d = datetime.strptime(from_time_str, '%H:%M') if single_date == from_date else datetime.strptime("00:00", '%H:%M')
                end = datetime.strptime(to_time_str, '%H:%M') if single_date == to_date else datetime.strptime("23:59", '%H:%M')
            while d < end:
                freeze = Freeze.objects.filter(facility_id=fid, date=single_date, time=time(hour=d.hour, minute=d.minute)).first()
                if freeze:
                    freeze.lock_count = freeze.lock_count - 1
                    if freeze.lock_count <= 0:
                        if freeze.is_order:
                            freeze.is_lock = False
                            freeze.save()
                        else:
                            freeze.delete()
                    else:
                        freeze.save()
                d += delta

        # Delete Lock Info
        lock_info = LockInfo.objects.filter(id=lid).first()
        lock_info.delete()

        return HttpResponse("", status=204)


@login_required(login_url="/login")
def get_lock_info(request, fid=None):
    if request.method == 'GET':
        today = date.today()
        lock_info_obj_list = LockInfo.objects.filter(
            facility_id=fid,
            to_date__gte=today,
        ).order_by('to_date')
        resp = {}
        lock_info_list = []
        for lock_info in lock_info_obj_list:
            lock_info_list.append({
                "id": lock_info.pk,
                "from_date": lock_info.from_date,
                "to_date": lock_info.to_date,
                "slot": lock_info.slot,
                "operator": lock_info.operator,
                "lock_type": lock_info.lock_type
            })
        resp['lock_info_list'] = lock_info_list
        resp['current_login_user'] = {
            "username": request.user.username,
            "is_super_admin": request.user.is_super_admin
        }
        return JsonResponse(resp, safe=False)
