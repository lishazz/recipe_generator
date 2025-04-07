from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path("addreview_rating/<int:recipe_id>/", views.addreview_rating, name="addreview_rating"),
    path('generate_recipe/',views.generate_recipe,name='generate_recipe'),
    path('nutritional_info/<int:recipe_id>/', views.nutritional_info, name='nutritional_info'),
    path('user_settings/',views.user_settings,name='user_settings'),
    # path('user_view_recipe/',views.user_view_recipe,name='user_view_recipe'),
    path('favourite_recipe/',views.favourite_recipe,name='favourite_recipe'),
    path("recipe/<int:recipe_id>/", views.user_view_recipe, name='user_view_recipe'),
    path('recipe/<int:recipe_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('search/', views.search_recipe, name='search_recipe'),
]