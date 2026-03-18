from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("register/", views.register, name="register"),
    path('login/', views.login_view),
    path('get_app_info/', views.get_app_info),
    path('admin_get_app_info/', views.admin_get_app_info),
    path("download_users/", views.download_users, name="download_users")
]