from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return HttpResponse("Logged in!")

        return HttpResponse("Login failed")

    return render(request, "login.html")


def get_app_info(request):
    return HttpResponse("Public info")


# OWASP 2021 1: Broken access control
# There is no authentication check for sensitive admin info
def admin_get_app_info(request):
    return HttpResponse("Sensitive admin data: only admins should see this")


# FIX:
# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def admin_get_app_info(request):
    # return HttpResponse("Sensitive admin info: only admins should see this")