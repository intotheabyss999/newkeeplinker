from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'auth_app'

urlpatterns = [
    # User-related views
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Password change views
    path('password_change/', views.change_password, name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='auth_app/password_change_done.html'), name='password_change_done'),

    # Password reset views (for "Forgot Password" functionality)
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),  # Using custom view
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth_app/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Using custom view for confirmation
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='auth_app/password_reset_complete.html'), name='password_reset_complete'),
]
