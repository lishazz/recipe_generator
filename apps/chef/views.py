from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.common.decorator import chef_required
from .forms import RecipeForm,IngredientFormSet,ChefSettingsForm
from apps.common.models import Recipe,Ingredient,RecipeIngredient,Rating,ReviewReply
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_required
@chef_required
def chef_dashboard(request):
    # Get all recipes by the chef
    chef_recipes = Recipe.objects.filter(created_by=request.user)
    
    # Get the total count
    total_recipes = chef_recipes.count()

    total_system_recipes = Recipe.objects.all().count()
    
    # Calculate total average rating
    total_avg_rating = Recipe.objects.filter(
        created_by=request.user,
        ratings__isnull=False
    ).aggregate(
        total_avg=models.Avg('ratings__rating')
    )['total_avg'] or 0
    
    # Get the ratings data
    recipes_with_ratings = chef_recipes.annotate(
        avg_rating=models.Avg('ratings__rating')
    ).values('title', 'avg_rating')
    
    # Convert to list and handle None values
    recipes_data = [
        {
            'title': recipe['title'],
            'avg_rating': float(recipe['avg_rating']) if recipe['avg_rating'] else 0
        }
        for recipe in recipes_with_ratings
    ]
    
    context = {
        'user': request.user,
        'chef_recipes': json.dumps(recipes_data, cls=DjangoJSONEncoder),
        'total_recipes': total_recipes,
        'total_avg_rating': round(float(total_avg_rating), 1),
        'total_system_recipes':total_system_recipes,
     }
    return render(request, 'chef_dashboard.html', context)

@login_required
@chef_required
def create_recipe(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        ingredient_formset = IngredientFormSet(request.POST)

        if form.is_valid() and ingredient_formset.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()

            for ingredient_form in ingredient_formset:
                name = ingredient_form.cleaned_data.get("ingredient_name")
                quantity = ingredient_form.cleaned_data.get("ingredient_quantity")

                if name and quantity:  # Ensure valid data
                    ingredient, created = Ingredient.objects.get_or_create(name=name.lower())
                    RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=quantity)

            return redirect('view_myrecipe')  # Redirect to recipe list

    else:
        form = RecipeForm()
        ingredient_formset = IngredientFormSet()

    return render(request, 'create_recipe.html', {'form': form, 'ingredient_formset': ingredient_formset})

@login_required
@chef_required
def view_review(request):
    # Get all recipes created by the logged-in chef
    recipes = Recipe.objects.filter(created_by=request.user)

    # Get reviews for those recipes
    ratings = Rating.objects.filter(recipe__in=recipes)

    return render(request, 'view_review.html', {"ratings": ratings})


@login_required
@chef_required
def view_myrecipe(request):
    if request.user.is_authenticated:
        recipes = Recipe.objects.filter(created_by=request.user)  # Filter recipes by logged-in user
    else:
        recipes = None  # No recipes if the user is not logged in

    return render(request, 'view_myrecipe.html', {'recipes': recipes})

@login_required
@chef_required
def recipe_detail(request, recipe_id):
    """Display the details of a specific recipe."""
    recipe = get_object_or_404(Recipe, id=recipe_id, created_by=request.user)
    return render(request, 'recipe_detail.html', {'recipe': recipe})


@login_required
@chef_required
def edit_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)  # Use instance
        if form.is_valid():
            form.save()  # No need to reassign created_by; it's already set
            return redirect("chef_dashboard")
    else:
        form = RecipeForm(instance=recipe)  # Prepopulate form with recipe data

    return render(request, "edit_recipe.html", {"form": form, "recipe": recipe})


@login_required
@chef_required
def delete_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == "POST":
        recipe.delete()
        return redirect('chef_dashboard')
    
@login_required
@chef_required
def add_review_reply(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)
    if request.method == "POST":
        reply_text = request.POST.get('reply_text')
        if reply_text:
            ReviewReply.objects.create(
                rating=rating,
                chef=request.user,
                reply_text=reply_text
            )
    return redirect('view_review')
@login_required
@chef_required
def chef_settings(request):
    if request.method == 'POST':
        form = ChefSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']

            # Verify current password
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
                return render(request, 'chef_settings.html', {'form': form})

            # Save email changes
            user = form.save(commit=False)
            
            # Update password if provided
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep user logged in
            
            user.save()
            messages.success(request, 'Your settings have been updated successfully')
            return redirect('chef_dashboard')
    else:
        form = ChefSettingsForm(instance=request.user)
    
    return render(request, 'chef_settings.html', {'form': form})