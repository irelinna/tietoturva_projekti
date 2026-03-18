from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from .models import SimpleUser

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
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = SimpleUser.objects.get(username=username)

            # FLAW: weak password verification
            if user.check_password(password):
                request.session['user'] = user.username
                return HttpResponse("Logged in!")

        except SimpleUser.DoesNotExist:
            pass

        return HttpResponse("Login failed")

    return render(request, "login.html")


# FIX: use Django authentication
# def login_view(request):
#     # OWASP 2021 2: Cryptographic failures 
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # FIX: Use Django's secure authentication
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return HttpResponse("Logged in!")

#         return HttpResponse("Login failed")

#     return render(request, "login.html")



def register(request):
    # OWASP 2021 2: Cryptographic failures
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = SimpleUser(username=username)

        # FLAW: weak hashing
        user.set_password(password)

        user.save()

        return HttpResponse("User created")

    return render(request, "register.html")


# FIX:
# def register(request):
#    # OWASP 2021 2: Cryptographic failures
#    if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         # FIX: Use Django's built-in secure user creation
#         user = SimpleUser.objects.create_user(username=username, password=password)
#         user.save()

#         return HttpResponse("User created")

#     return render(request, "register.html")


def download_users(request):
    # OWASP 2021 2: Cryptographic failures
    # FLAW: exposes password hashes without authentication
    users = SimpleUser.objects.all()

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

#     users = SimpleUser.objects.all()
#     data = ""
#     for user in users:
#         # Passwords are stored securely, cannot retrieve raw hashes
#         data += f"{user.username}: (protected)\n"

#     return HttpResponse(data, content_type="text/plain")




# OWASP 2021 3: SQL injection 
def get_user(request):
    user_id = request.GET.get('id')

    # # FLAW: user input inserted directly into query
    # query = f"SELECT * FROM polls_simpleuser WHERE id = '{user_id}'"

    # with connection.cursor() as cursor:
    #     cursor.execute(query)
    #     result = cursor.fetchall()
    #     if not result:
    #        return HttpResponse("No results found")

    # data = "<br>".join([str(row) for row in result])
    # return HttpResponse(data)

    # FIX: parameterized query prevents SQL injection
    query = "SELECT * FROM polls_simpleuser WHERE id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, [user_id])
        result = cursor.fetchall()
        if not result:
            return HttpResponse("No results found")
    
    data = "<br>".join([str(row) for row in result])
    return HttpResponse(data)
