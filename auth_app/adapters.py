import logging
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from collections_app.models import Collection
from auth_app.models import UserProfile

logger = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated:
            user_collections = Collection.objects.filter(user=user)
            logger.debug("User %s has %d collections.", user.email, user_collections.count())
            
            if user_collections.count() == 0:
                return '/collections/create/'
            elif user_collections.count() == 1:
                collection = user_collections.first()
                return f'/collections/{collection.id}/'
            else:
                return '/collections/list/'
        return '/'

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        # Add any custom fields you want to save from the signup form here
        if commit:
            user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # This method is called before the user is logged in via social account
        if not sociallogin.is_existing:
            # This is a new user
            request.session['new_social_user'] = True
        logger.debug("Pre-social login for user: %s, is_existing: %s", 
                     sociallogin.user.email, sociallogin.is_existing)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        
        # Create or update UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Get profile picture URL
        if sociallogin.account.provider == 'facebook':
            picture_url = sociallogin.account.extra_data.get('picture', {}).get('data', {}).get('url')
        elif sociallogin.account.provider == 'google':
            picture_url = sociallogin.account.extra_data.get('picture')
        else:
            picture_url = None
        
        if picture_url:
            profile.profile_picture = picture_url
            profile.save()
        
        if request.session.pop('new_social_user', False):
            # This is a new user, set flag for redirection
            request.session['redirect_to_collection_create'] = True
        logger.debug("Saved social user: %s, redirect flag: %s", 
                     user.email, request.session.get('redirect_to_collection_create', False))
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        return self.get_login_redirect_url(request)

    def get_login_redirect_url(self, request):
        if request.session.pop('redirect_to_collection_create', False):
            logger.debug("Redirecting new social user to collection creation")
            return '/collections/create/'
        return CustomAccountAdapter().get_login_redirect_url(request)

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # You can add custom user data here if needed
        return user