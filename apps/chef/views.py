from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from apps.common.decorator import chef_required
from .forms import RecipeForm
@login_required
@chef_required
def chef_dashboard(request):
    return render(request, "chef_dashboard.html")

@login_required
@chef_required
def create_recipe(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)  # Don't save yet
            recipe.created_by = request.user  # Assign the logged-in user
            recipe.save()  # Now save with the user
            return redirect("chef_dashboard")  # Redirect after successful save
    else:
        form = RecipeForm()  # Instantiate an empty form
    
    return render(request, "create_recipe.html", {"form": form})


@login_required
@chef_required
def view_review(request):
    return render(request,'view_review.html')

@login_required
@chef_required
def view_myrecipe(request):
    return render(request,"view_myrecipe.html")
