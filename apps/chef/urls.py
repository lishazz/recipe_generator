from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('chef_dashboard/', views.chef_dashboard, name='chef_dashboard'),
    path('create_recipe/',views.create_recipe,name="create_recipe"),
    path('view_review/',views.view_review,name="view_review"),
    path('view_myrecipe/', views.view_myrecipe, name='view_myrecipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/edit/<int:id>/', views.edit_recipe, name='edit_recipe'),
    path('recipe/delete/<int:id>/', views.delete_recipe, name='delete_recipe'),
]