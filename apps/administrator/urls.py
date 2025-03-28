from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('administrator_dashboard/', views.administrator_dashboard, name='administrator_dashboard'),
    path('approve_chef/',views.approve_chef,name='approve_chef'),
    path('manage_user/',views.manage_user,name='manage_user')
]