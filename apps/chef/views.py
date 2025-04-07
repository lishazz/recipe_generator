from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.common.decorator import chef_required
from .forms import RecipeForm,IngredientFormSet
from apps.common.models import Recipe,Ingredient,RecipeIngredient,Rating
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required
@chef_required
def chef_dashboard(request):
    chef_recipes = Recipe.objects.filter(created_by=request.user).annotate(
        avg_rating=models.Avg('ratings__rating')
    ).values('title', 'avg_rating')
    
    # Convert to list and handle None values
    recipes_data = [
        {
            'title': recipe['title'],
            'avg_rating': float(recipe['avg_rating']) if recipe['avg_rating'] else 0
        }
        for recipe in chef_recipes
    ]
    
    context = {
        'user': request.user,
        'chef_recipes': json.dumps(recipes_data, cls=DjangoJSONEncoder)
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
    

