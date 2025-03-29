from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.common.decorator import administrator_required
from apps.common.models import User
from django.contrib import messages

@login_required
@administrator_required
def administrator_dashboard(request):
    return render(request, "administrator_dashboard.html")


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