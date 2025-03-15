from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'), 
    path('login/', views.login_view, name='login_page'),
    path('register/', views.register, name='register'),
    path('login/forget_pass/', views.forget_pass, name='forget_pass'),
    path('logout/', views.logout_view, name='logout'),
]