from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.common.decorator import chef_required

@login_required
@chef_required
def chef_dashboard(request):
    return render(request, "chef_dashboard.html")

def create_recipe(request):
    return render(request,'create_recipe.html')

def view_review(request):
    return render(request,'view_review.html')