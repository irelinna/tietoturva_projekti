from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from .models import User
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import hashlib

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


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



def login_view(request):
    # OWASP 2021 2: Cryptographic failures
    # OWASP 2021 7: Identification and authentication failures
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)

            # FLAW: weak password verification, no account lockout, no logging
            if user.check_password(password):
                request.session['user'] = user.username
                return HttpResponse("Logged in!")

        except User.DoesNotExist:
            pass

        return HttpResponse("Login failed")

    return render(request, "login.html")


# FIX: 
# def login_view(request):
#     # OWASP 2021 2: Cryptographic failures 
#     # OWASP 2021 7: Identification and authentication failures
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # FIX: Use Django's secure authentication
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)  # Django manages session securely
#             return HttpResponse("Logged in!")
#         # Log failed attempts and enforce lockout
#         return HttpResponse("Login failed")

#     return render(request, "login.html")



def register(request):
    # OWASP 2021 2: Cryptographic failures
    # OWASP 2021 7: Identification and authentication failures
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User(username=username)

        # FLAW: weak hashing
        user.set_password(password)

        user.save()

        return HttpResponse("User created")

    return render(request, "register.html")


# FIX:
# def register(request):
#    # OWASP 2021 2: Cryptographic failures
#    # OWASP 2021 7: Identification and authentication failures
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         # FIX: Use Django's built-in secure user creation + password validation
#         try:
#             validate_password(password)  # enforce complexity
#             user = User.objects.create_user(username=username, password=password)
#             user.save()
#             return HttpResponse("User created")
#         except ValidationError as e:
#             return HttpResponse(f"Password not strong enough: {e}")
#     return render(request, "register.html")


def download_users(request):
    # OWASP 2021 2: Cryptographic failures
    # FLAW: exposes password hashes without authentication
    users = User.objects.all()

    data = ""
    for user in users:
        data += f"{user.username}:{user.password}\n"

    return HttpResponse(data, content_type="text/plain")


# FIX:
# def download_users(request):
#     # OWASP 2021 2: Cryptographic failures
#     # FIX: restrict access to admins only
#     if not request.user.is_authenticated or not request.user.is_staff:
#         return HttpResponse("Unauthorized", status=403)

#     users = User.objects.all()
#     data = ""
#     for user in users:
#         # Passwords are stored securely, cannot retrieve raw hashes
#         data += f"{user.username}: (protected)\n"

#     return HttpResponse(data, content_type="text/plain")




# OWASP 2021 3: SQL injection 
def get_user(request):
    user_id = request.GET.get('id')

    # # FLAW: user input inserted directly into query
    query = f"SELECT * FROM polls_user WHERE id = '{user_id}'"

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
           return HttpResponse("No results found")

    data = "<br>".join([str(row) for row in result])
    return HttpResponse(data)

    # FIX: parameterized query prevents SQL injection
    # query = "SELECT * FROM polls_user WHERE id = %s"
    # with connection.cursor() as cursor:
    #     cursor.execute(query, [user_id])
    #     result = cursor.fetchall()
    #     if not result:
    #         return HttpResponse("No results found")
    
    # data = "<br>".join([str(row) for row in result])
    # return HttpResponse(data)
