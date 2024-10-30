from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm
from collections_app.models import Collection , User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm , CustomPasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView  # Import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
import logging
from django.core.exceptions import MultipleObjectsReturned
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.db import connection



# # Sign-up view
# def signup(request):
#     logger.debug("Signup view initiated.")  # Log the start of the signup view

#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)  # Log the user in immediately after signup
#             logger.debug("User signed up and logged in: %s", user.email)  # Log successful signup
#             return redirect('collections_app:create_collection')
#     else:
#         form = SignUpForm()

#     try:
#         google_app = SocialApp.objects.get(provider='google', sites__id=settings.SITE_ID)
#         logger.debug("Google app found: %s", google_app)  # Log if Google app is found
#     except MultipleObjectsReturned:
#         logger.error("Multiple Google apps found for site ID: %s", settings.SITE_ID)
#         messages.error(request, "Configuration error: multiple Google apps found.")
#     except SocialApp.DoesNotExist:
#         logger.error("Google app does not exist for site ID: %s", settings.SITE_ID)
#         messages.error(request, "Google authentication configuration is missing.")
    
#     logger.debug("Rendering signup page.")
    
#     return render(request, 'auth_app/signup.html', {'form': form})


logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Authenticate the user
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            
            # Ensure the correct backend is specified for login
            if user is not None:
                # If the user was authenticated successfully
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # Explicitly set the backend
                login(request, user)
                return redirect('collections_app:create_collection')  # Redirect to collection creation
    else:
        form = SignUpForm()

    return render(request, 'auth_app/signup.html', {'form': form})

def signin(request):
    if request.method == "POST":
        email = request.POST['username']
        password = request.POST['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'auth_app/signin.html', {'error': 'Invalid email or password'})
        
        user = authenticate(request, username=user.username, password=password)
        
        if user is not None:
            login(request, user)
            
            user_collections = Collection.objects.filter(user=user)
            if user_collections.count() == 0:
                return redirect('collections_app:create_collection')  # Updated
            elif user_collections.count() == 1:
                collection = user_collections.first()
                return redirect('collections_app:collection_details', collection_id=collection.id)  # Updated
            else:
                return redirect('collections_app:collections_list')  # Updated
        else:
            return render(request, 'auth_app/signin.html', {'error': 'Invalid email or password'})
    
    return render(request, 'auth_app/signin.html')


@login_required
def profile(request):
    return render(request, 'auth_app/profile.html')

# Custom password change
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to prevent logout after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('auth_app:password_change_done')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'auth_app/change_password.html', {
        'form': form
    })


# Custom Password Reset View
class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'auth_app/password_reset.html'
    email_template_name = 'auth_app/password_reset_email.html'
    subject_template_name = 'auth_app/password_reset_subject.txt'
    success_message = "We've emailed you instructions for resetting your password."
    success_url = reverse_lazy('auth_app:password_reset_done')
    form_class = CustomPasswordResetForm

# Custom Password Reset Confirm View
class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):  # Imported PasswordResetConfirmView
    template_name = 'auth_app/password_reset_confirm.html'
    success_url = reverse_lazy('auth_app:password_reset_complete')
    success_message = "Your password has been reset."
