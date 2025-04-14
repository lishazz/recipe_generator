from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.common.decorator import user_required
from .forms import IngredientForm, UserSettingsForm
from apps.aistudio.utils import generate
from django.db import IntegrityError
from titlecase import titlecase
from apps.common.models import User, Recipe, GenerateRecipe, Ingredient, RecipeIngredient,Rating,FavoriteRecipe, ChefRating
import json
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db import models
from django.db.models import Avg, Count

@login_required
@user_required
def user_dashboard(request):
    recipe_list = Recipe.objects.annotate(
        avg_rating=models.Avg('ratings__rating')
    ).order_by('-avg_rating')  
    chef_recipes = Recipe.objects.filter(ai_generated=False)
    
    context = {
        "recipe_list":recipe_list,
        "chef_recipes": chef_recipes
    }
    return render(request,'user_dashboard.html', context)

@login_required
@user_required
def search_recipe(request):
    if request.method == "POST":
        search_query = request.POST.get('search_query', '').strip()
        if search_query:
            # Search in title, description, and category with rating annotation
            recipe_list = Recipe.objects.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(category__icontains=search_query) 
            ).annotate(
                avg_rating=models.Avg('ratings__rating')
            ).order_by('-avg_rating')
        else:
            # If no search query, return all recipes ordered by rating
            recipe_list = Recipe.objects.annotate(
                avg_rating=models.Avg('ratings__rating')
            ).order_by('-avg_rating')
    else:
        # For GET requests, show all recipes ordered by rating
        recipe_list = Recipe.objects.annotate(
            avg_rating=models.Avg('ratings__rating')
        ).order_by('-avg_rating')

    # Split recipes into chef and AI-generated categories
    chef_recipes = recipe_list.filter(ai_generated=False)
    ai_recipes = recipe_list.filter(ai_generated=True)

    context = {
        "chef_recipes": chef_recipes,
        "recipe_list": ai_recipes,
        "search_query": search_query if request.method == "POST" else ""
    }
    return render(request, 'user_dashboard.html', context)


@login_required
def addreview_rating(request, recipe_id):  # Expect recipe_id as a parameter
    recipe = get_object_or_404(Recipe, id=recipe_id)  # Fetch recipe safely

    if request.method == "POST":
        review_text = request.POST.get("review")
        rating_value = request.POST.get("rating")

        if not rating_value:
            messages.error(request, "Please select a rating.")
            return redirect(f"/addreview/{recipe.id}")

        # Ensure rating is valid
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                raise ValueError
        except ValueError:
            messages.error(request, "Invalid rating value.")
            return redirect(f"/addreview/{recipe.id}")

        # Check if the user has already rated the recipe
        existing_rating = Rating.objects.filter(user=request.user, recipe=recipe).first()
        if existing_rating:
            existing_rating.rating = rating_value
            existing_rating.review = review_text
            existing_rating.save()
            messages.success(request, "Your review has been updated.")
        else:
            Rating.objects.create(user=request.user, recipe=recipe, rating=rating_value, review=review_text)
            messages.success(request, "Review submitted successfully.")

        return redirect('user_view_recipe', recipe_id)  # Redirect to recipe page

    return render(request, "addreview_rating.html", {"recipe": recipe})



@login_required
def generate_recipe(request):
    form = IngredientForm()
    title = ""
    description = ""
    recipe_category = ""
    ingredients = []
    ingredient_category= ""
    instructions = ""
    ingredients_list = []
    cooking_time = 10  # Default value as an integer

    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            # Get and process ingredients
            ingredients_input = form.cleaned_data["ingredients"]
            ingredients_list = [ingredient.strip() for ingredient in ingredients_input.split(",")]

            # Generate recipe using AI
            generated_recipe = generate(ingredients_list)
            # print(generated_recipe)

            # Extract data from response
            title = generated_recipe.get('response', {}).get('RecipeTitle', "Untitled Recipe")
            description = generated_recipe.get('response',{}).get('Description',[])
            recipe_category = generated_recipe.get('response',{}).get('Category',[])
            instructions = generated_recipe.get('response', {}).get('Instructions', [])
            ingredients =  generated_recipe.get('response',{}).get('Ingredients',[])
            print(ingredients)
            # ingredient_category =
            # Ensure cook_time is always an integer
            cooking_time = generated_recipe.get('response', {}).get('CookingTime', None)

            if cooking_time is None or cooking_time == "":  # Handle missing or empty cook_time
                cooking_time = 10  # Default to 10 minutes
            else:
                try:
                    cooking_time = int(cooking_time)  # Convert to integer
                except ValueError:
                    cooking_time = 10  # Default if conversion fails

            # Save Recipe in the database
            recipe, created = Recipe.objects.get_or_create(
                title=title,
                description=description,
                category=recipe_category,
                defaults={
                    "instruction": "\n".join([step["content"] for step in instructions]),
                    "cook_time": cooking_time,  # Ensured integer value
                    "created_by": request.user,
                    "ai_generated": True
                }
            )

            # Save ingredients and link them to the recipe


            for item in ingredients:
                try:
                    if not isinstance(item, dict) or 'name' not in item:
                        print(f"Skipping invalid ingredient: {item}")
                        continue  # Skip if the format is incorrect
                    
                    # Get or create ingredient by name
                    ingredient, created = Ingredient.objects.get_or_create(name=titlecase(item['name']))
            
                    # Update ingredient details if they exist in the API response
                    ingredient.category = item.get('category', ingredient.category)
                    ingredient.calories_per_100g = item.get('calories', ingredient.calories_per_100g)
                    ingredient.carbs_per_100g = item.get('carbohydrates', ingredient.carbs_per_100g)
                    ingredient.protein_per_100g = item.get('protein', ingredient.protein_per_100g)
                    ingredient.fats_per_100g = item.get('fats', ingredient.fats_per_100g)
                    ingredient.save()  # Ensure updates are saved
            
                    # Link ingredient to the recipe
                    RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=item.get('quantity',100))
            
                    print(f"Saved ingredient: {ingredient.name} - {ingredient.category}")
            
                except IntegrityError:
                    print(f"Duplicate entry error for ingredient: {item.get('name', 'Unknown')}")
                except Exception as e:
                    print(f"Error processing ingredient {item}: {e}")
            

            # Log user-generated recipes
            GenerateRecipe.objects.create(user=request.user, user_input_ingredients=", ".join(ingredients_list), recipe=recipe)

            return redirect("user_view_recipe", recipe_id=recipe.id)  # Redirect to a detail page

    return render(request, "generate_recipe.html", {
        "form": form,
        "title": title,
        "description":description,
        "category":recipe_category,
        "ingredients": ingredients_list,
        "instructions": instructions,
        "cook_time": cooking_time,
    })



@login_required
@user_required
def nutritional_info(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    
    # Calculate total nutritional values
    total_calories = 0
    total_proteins = 0
    total_carbs = 0
    total_fats = 0
    
    for recipe_ingredient in recipe_ingredients:
        # Get quantity in grams and multiply by per 100g values
        quantity_factor = recipe_ingredient.quantity / 100
        total_calories += recipe_ingredient.ingredient.calories_per_100g * quantity_factor
        total_proteins += recipe_ingredient.ingredient.protein_per_100g * quantity_factor
        total_carbs += recipe_ingredient.ingredient.carbs_per_100g * quantity_factor
        total_fats += recipe_ingredient.ingredient.fats_per_100g * quantity_factor
    
    nutritional_info = {
        'id': recipe.id,
        'name': recipe.title,
        'calories': round(total_calories, 2),
        'proteins': round(total_proteins, 2),
        'carbohydrates': round(total_carbs, 2),
        'fats': round(total_fats, 2)
    }
    
    return render(request, 'nutritional_info.html', {'recipe': nutritional_info})

@login_required
@user_required
def user_settings(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']

            # Verify current password
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
                return render(request, 'user_settings.html', {'form': form})

            # Save email changes
            user = form.save(commit=False)
            
            # Update password if provided
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep user logged in
            
            user.save()
            messages.success(request, 'Your settings have been updated successfully')
            return redirect('user_dashboard')
    else:
        form = UserSettingsForm(instance=request.user)
    
    return render(request, 'user_settings.html', {'form': form})

@login_required
@user_required
def user_view_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    ratings = Rating.objects.filter(recipe=recipe).prefetch_related('replies').order_by('-created_at')

    return render(request, "user_view_recipe.html", {
        "recipe": recipe,
        "ingredients": ingredients,
        "ratings": ratings
    })

@login_required
@user_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite, created = FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)

    if not created:
        favorite.delete()
        messages.success(request, "Removed from favorites")
    else:
        messages.success(request, "Added to favorites")

    return redirect('user_view_recipe', recipe_id=recipe.id)


def favourite_recipe(request):
    favourite_recipes = Recipe.objects.all()  # Update with actual filtering logic
    return render(request, 'favourite_recipe.html', {'favourite_recipes': favourite_recipes})

@login_required
def rate_chef(request, chef_id):
    chef = get_object_or_404(User, id=chef_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')
        
        if not rating:
            messages.error(request, 'Please provide a rating.')
            return redirect('chef_detail', chef_id=chef_id)
        
        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid rating value. Please rate between 1 and 5.')
            return redirect('chef_detail', chef_id=chef_id)
        
        chef_rating, created = ChefRating.objects.update_or_create(
            chef=chef,
            user=request.user,
            defaults={
                'rating': rating,
                'feedback': feedback
            }
        )
        
        action = 'updated' if not created else 'submitted'
        messages.success(request, f'Rating {action} successfully!')
        return redirect('chef_detail', chef_id=chef_id)
    return redirect('chef_detail', chef_id=chef_id)


@login_required
def chef_detail(request, chef_id):
    """View for single chef details"""
    chef = User.objects.filter(id=chef_id).annotate(
        recipe_count=Count('recipes', distinct=True),
        avg_rating=Avg('recipes__ratings__rating'),
        total_ratings=Count('recipes__ratings', distinct=True)
    ).first()
    
    if not chef:
        raise Http404("Chef not found")
    
    # Get recipes created by this chef with their ratings
    recipes = Recipe.objects.filter(created_by=chef).annotate(
        avg_rating=Avg('ratings__rating')
    )
    
    context = {
        'chef': chef,
        'recipes': recipes,
        'single_chef': True
    }
    return render(request, 'chef_details.html', context)

@login_required
def chef_details_list(request):
    """View for listing all chefs"""
    chefs = User.objects.filter(role='chef').annotate(
        recipe_count=Count('recipes', distinct=True),
        avg_rating=Avg('received_ratings__rating'),
        total_ratings=Count('received_ratings', distinct=True),
        rating_5=Count('received_ratings', filter=models.Q(received_ratings__rating=5), distinct=True),
        rating_4=Count('received_ratings', filter=models.Q(received_ratings__rating=4), distinct=True),
        rating_3=Count('received_ratings', filter=models.Q(received_ratings__rating=3), distinct=True),
        rating_2=Count('received_ratings', filter=models.Q(received_ratings__rating=2), distinct=True),
        rating_1=Count('received_ratings', filter=models.Q(received_ratings__rating=1), distinct=True)
    ).prefetch_related('recipes', 'received_ratings')
    
    # Calculate rating percentages for each chef
    for chef in chefs:
        chef.rating_percentages = {
            5: (chef.rating_5 / chef.total_ratings * 100) if chef.total_ratings > 0 else 0,
            4: (chef.rating_4 / chef.total_ratings * 100) if chef.total_ratings > 0 else 0,
            3: (chef.rating_3 / chef.total_ratings * 100) if chef.total_ratings > 0 else 0,
            2: (chef.rating_2 / chef.total_ratings * 100) if chef.total_ratings > 0 else 0,
            1: (chef.rating_1 / chef.total_ratings * 100) if chef.total_ratings > 0 else 0
        }
    
    context = {
        'chefs': chefs,
        'single_chef': False
    }
    return render(request, 'chef_details.html', context)
