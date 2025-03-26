from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('toggle-chef/<int:user_id>/', views.toggle_chef_status, name='toggle_chef_status'),
    path('administrator_dashboard/', views.administrator_dashboard, name='administrator_dashboard'),
    path('approve_chef/',views.approve_chef,name='approve_chef'),
    path('manage_user/',views.manage_user,name='manage_user')
]