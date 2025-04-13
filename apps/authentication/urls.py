from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'), 
    path('login/', views.login_view, name='login_page'),
    path('register/', views.register, name='register'),
    path('forgot_password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),
        path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/login'  # Or use reverse_lazy
        ),
        name='password_reset_confirm'
    ),
]