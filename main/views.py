from django.shortcuts import render, redirect
from django.http import HttpResponse
from collections_app.models import Collection
from django.contrib.auth.decorators import login_required

def index(request):
    if request.user.is_authenticated:
        if request.session.pop('new_social_user', False):
            return redirect('collections_app:create_collection')
        
        user_collections = Collection.objects.filter(user=request.user)
        if user_collections.count() == 0:
            return redirect('collections_app:create_collection')
        elif user_collections.count() == 1:
            collection = user_collections.first()
            return redirect('collections_app:collection_details', collection_id=collection.id)
        else:
            return redirect('collections_app:collections_list')
    
    # If user is not authenticated, show the index page
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def signin(request):
    if request.user.is_authenticated:
        return redirect('collections_app:collections_list')
    return render(request, 'auth_app/signin.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('collections_app:collections_list')
    return render(request, 'auth_app/signup.html')

def terms(request):
    return render(request, 'main/terms.html')

def privacy(request):
    return render(request, 'main/privacy.html')

@login_required
def dashboard(request):
    user_collections = Collection.objects.filter(user=request.user)
    if user_collections.count() == 0:
        return redirect('collections_app:create_collection')
    elif user_collections.count() == 1:
        collection = user_collections.first()
        return redirect('collections_app:collection_details', collection_id=collection.id)
    else:
        return redirect('collections_app:collections_list')