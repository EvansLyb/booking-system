# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Kyle
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .forms import LoginForm, SignUpForm


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/dashboard/account/list")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


# def login_view(request):
#     msg = None

#     if request.method == "POST":
#         json_data = json.loads(request.body)
#         username = json_data.get('username')
#         password = json_data.get('password')

#         if username and password:
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return JsonResponse({"status": 200})
#             else:
#                 msg = 'Invalid credentials'
#         else:
#             msg = 'Invalid username or password'

#     return JsonResponse({"msg": msg}, status=400)


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
