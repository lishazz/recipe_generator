from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from apps.common.decorator import user_required
from .forms import IngredientForm
from apps.aistudio.utils import generate
from django.db import IntegrityError
from titlecase import titlecase
from apps.common.models import Recipe, GenerateRecipe, Ingredient, RecipeIngredient
import json

@login_required
@user_required
def user_dashboard(request):
    return render(request,'user_dashboard.html')


@login_required
@user_required
def addreview_rating(request):
    return render(request,"addreview_rating.html")

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .forms import IngredientForm

# from .recipe_generator import generate  # Ensure this function generates recipes

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
def favourite_recipe(request):
    return render(request,'favourite_recipe.html')