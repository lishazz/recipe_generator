from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.common.decorator import chef_required

@login_required
@chef_required
def chef_dashboard(request):
    return render(request, "chef_dashboard.html")


@login_required
@chef_required
def create_recipe(request):
    return render(request,'create_recipe.html')


@login_required
@chef_required
def view_review(request):
    return render(request,'view_review.html')

@login_required
@chef_required
def view_myrecipe(request):
    return render(request,"view_myrecipe.html")
