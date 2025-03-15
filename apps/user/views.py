from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.common.decorator import user_required
from .forms import IngredientForm

@login_required
@user_required
def user_dashboard(request):
    return render(request,'user_dashboard.html')


@login_required
@user_required
def addreview_rating(request):
    return render(request,"addreview_rating.html")

@login_required
@user_required
def generate_recipe(request):
    form = IngredientForm()
    recipes = []
    ingredients = []

    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredients_input = form.cleaned_data["ingredients"]
            ingredients = [ingredient.strip() for ingredient in ingredients_input.split(",")]
            # Logic to fetch recipes based on ingredients goes here
            # Example:
            # recipes = Recipe.objects.filter(ingredients__name__in=ingredients)

    return render(request, "generate_recipe.html", {
        "form": form,
        "recipes": recipes,
        "ingredients": ingredients
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
def user_view_recipe(request):
    return render(request,'user_view_recipe.html')

@login_required
@user_required
def favourite_recipe(request):
    return render(request,'favourite_recipe.html')