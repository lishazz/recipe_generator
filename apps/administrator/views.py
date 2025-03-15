from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.common.decorator import administrator_required

@login_required
@administrator_required
def administrator_dashboard(request):
    return render(request, "administrator_dashboard.html")


def approve_chef(request):
    return render(request,'approve_chef.html')

def manage_user(request):
    return render(request,'manage_user.html')
