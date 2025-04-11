from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.common.decorator import administrator_required
from apps.common.models import User,Recipe
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count
import json


@login_required
@administrator_required
def administrator_dashboard(request):
    total_recipes = Recipe.objects.count()
    total_chefs = User.objects.filter(role='chef').count()
    total_users = User.objects.filter(role='generaluser').count()
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_recipes_count = Recipe.objects.filter(created_at__gte=thirty_days_ago).count()
    
    active_chefs_count = Recipe.objects.filter(
        created_at__gte=thirty_days_ago,
        created_by__role='chef'
    ).values('created_by').distinct().count()
    
   
    fifteen_minutes_ago = timezone.now() - timedelta(minutes=15)
    online_users_count = User.objects.filter(
        last_login__gte=fifteen_minutes_ago
    ).count()
    
 
    top_rated_recipes = Recipe.objects.annotate(
        avg_rating=Avg('ratings__rating')  # Changed 'rating' to 'ratings'
    ).filter(
        avg_rating__isnull=False
    ).order_by('-avg_rating')[:5]
    
    top_rated_chefs = User.objects.filter(
        role='chef',
        recipes__isnull=False  # Only chefs with recipes
    ).annotate(
        avg_recipe_rating=Avg('recipes__ratings__rating')
    ).filter(
        avg_recipe_rating__isnull=False
    ).order_by('-avg_recipe_rating')[:5]

    all_recipes = Recipe.objects.all().select_related('created_by').annotate(
        avg_rating=Avg('ratings__rating')
    ).order_by('-created_at')

    chart_data = []
    chart_labels = []
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        count = Recipe.objects.filter(
            created_at__date=date.date()
                ).count()
        chart_data.append(count)
        chart_labels.append(date.strftime('%Y-%m-%d'))

    context = {
        'total_recipes': total_recipes,
        'total_chefs': total_chefs,
        'total_users': total_users,
        'new_recipes_count': new_recipes_count,
        'active_chefs_count': active_chefs_count,
        'online_users_count': online_users_count,
        'top_rated_recipes': top_rated_recipes,
        'top_rated_chefs': top_rated_chefs,
        'recent_recipes': Recipe.objects.order_by('-created_at')[:5],
        'all_recipes': all_recipes,
        'chart_data': json.dumps(chart_data),
        'chart_labels': json.dumps(chart_labels),
    }
    
    return render(request, "administrator_dashboard.html", context)


def approve_chef(request):
    chefs = User.objects.filter(role='chef')  # Get all chefs
    return render(request, 'approve_chef.html', {'chefs': chefs})

def manage_user(request):
    return render(request,'manage_user.html')

@login_required
@administrator_required
def toggle_chef_status(request, user_id):
    chef = get_object_or_404(User, id=user_id, role='chef')  # Ensure user is a chef
    chef.is_active = not chef.is_active  # Toggle status
    chef.save()
    status = "enabled" if chef.is_active else "disabled"
    messages.success(request, f"Chef {chef.username} has been {status}.")
    return redirect('approve_chef')  # Redirect to chef management page

@login_required
@administrator_required
def manage_recipes(request):
    recipes = Recipe.objects.all().select_related('created_by').annotate(
        avg_rating=Avg('ratings__rating')
    ).order_by('-created_at')
    return render(request, 'manage_recipes.html', {'recipes': recipes})


@login_required
@administrator_required
def view_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, 'view_recipe.html', {'recipe': recipe})



@login_required
@administrator_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully.')
        return redirect('manage_recipes')
    return redirect('manage_recipes')