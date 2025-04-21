from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('toggle-chef/<int:user_id>/', views.toggle_chef_status, name='toggle_chef_status'),
    path('administrator_dashboard/', views.administrator_dashboard, name='administrator_dashboard'),
    path('approve_chef/',views.approve_chef,name='approve_chef'),
    path('manage_user/',views.manage_user,name='manage_user'),
    path('manage_recipes/',views.manage_recipes,name='manage_recipes'),
    path('view-recipe/<int:recipe_id>/',views.view_recipe, name='view_recipe'),
    path('delete-recipe/<int:recipe_id>/',views.delete_recipe, name='delete_recipe'),
    path('toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-reviews/', views.manage_reviews, name='manage_reviews'),
]