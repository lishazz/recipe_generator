from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.common.decorator import user_required
from .forms import IngredientForm
from apps.aistudio.utils import generate
from django.db import IntegrityError
from titlecase import titlecase
from apps.common.models import Recipe, GenerateRecipe, Ingredient, RecipeIngredient,Rating,FavoriteRecipe
import json
from django.contrib import messages

@login_required
@user_required
def user_dashboard(request):
    recipe_list = Recipe.objects.all()
    context = {
        "recipe_list":recipe_list
    }
    return render(request,'user_dashboard.html', context)

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
def nutritional_info(request):
    return render(request,'nutritional_info.html')

@login_required
@user_required
def user_settings(request):
    return render(request,'user_settings.html')

@login_required
@user_required
def user_view_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)

    return render(request, "user_view_recipe.html", {
        "recipe": recipe,
        "ingredients": ingredients
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