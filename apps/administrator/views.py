from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.common.decorator import administrator_required
from apps.common.models import User
from django.contrib import messages

@login_required
@administrator_required
def administrator_dashboard(request):
    return render(request, "administrator_dashboard.html")

@login_required
@administrator_required
def approve_chef(request):
    chefs = User.objects.filter(role='chef')  # Get all chefs
    return render(request, 'approve_chef.html', {'chefs': chefs})

@login_required
@administrator_required
def manage_user(request):
    users = User.objects.filter(role='generaluser')  # Get all chefs
    return render(request,'manage_user.html',{'users': users})

@login_required
@administrator_required
def toggle_chef_status(request, user_id):
    chef = get_object_or_404(User, id=user_id, role='chef')  # Ensure user is a chef
    chef.is_active = not chef.is_active  # Toggle status
    chef.save()
    status = "enabled" if chef.is_active else "disabled"
    messages.success(request, f"Chef {chef.username} has been {status}.")
    return redirect('approve_chef')  # Redirect to chef management page


@login_required
@administrator_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        user.is_active = False
        messages.success(request, f"User {user.username} has been disabled.")
    else:
        user.is_active = True
        messages.success(request, f"User {user.username} has been enabled.")
    user.save()
    return redirect('manage_user')