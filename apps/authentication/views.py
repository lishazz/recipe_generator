from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model,authenticate, login , logout
from .forms import CustomUserCreationForm,LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request,'home.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                  # Change 'home' to your desired redirect page
                if user.is_superuser:
                    return redirect("administrator_dashboard")  # Superusers → Admin Dashboard
                elif user.role == "chef":
                    return redirect("chef_dashboard")  # Chefs → Chef Dashboard
                else:
                    return redirect("user_dashboard")

            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            # Log the user in (optional, if you want to log them in immediately)
            # from django.contrib.auth import login
            # login(request, user)
            messages.success(request, 'Registration successful!') # Optional success message
            print("Registration successful!")
            return redirect('login_page') # Redirect to login page (replace 'login' with your login URL name)
        else:
            # Form is invalid, display errors.  Crucially important.
            messages.error(request, 'Registration failed. Please correct the errors below.')
            print("Registration Failed!")
            return render(request, 'register.html', {'form': form})
    else:
        form = CustomUserCreationForm()  # Create a blank form for GET request.

    return render(request, 'register.html', {'form': form})

def forget_pass(request):
    return render(request,'forget_pass.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login_page")