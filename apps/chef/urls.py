from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('chef_dashboard/', views.chef_dashboard, name='chef_dashboard'),
    path('create_recipe/',views.create_recipe,name="create_recipe"),
    path('view_review/',views.view_review,name="view_review"),
]