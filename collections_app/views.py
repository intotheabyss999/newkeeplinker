from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests, random
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .models import Collection, Link
from .forms import CollectionForm, LinkForm
from django.urls import reverse
from django.contrib import messages
from favicon import get as get_favicon
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q


# A list of available images, randomly assigned during collection creation
COLLECTION_IMAGES = [
    'example1.svg', 'example2.svg', 'example3.svg', 'example4.svg' ,  'example5.svg', 'example6.svg', 'example7.svg', 'example8.svg', 'example9.svg', 'example10.svg', 'example11.svg', 'example12.svg', 'example13.svg', 'example14.svg', 'example15.svg', 'example16.svg', 'example17.svg', 'example18.svg', 'example19.svg', 'example20.svg', 'example21.svg', 'example22.svg', 'example23.svg', 'example24.svg', 'example25.svg', 'example26.svg', 'example27.svg', 'example28.svg', 'example29.svg', 'example30.svg', 'example31.svg', 'example32.svg', 'example33.svg'
]

# Existing collection list view
@login_required
def collections_list(request):
    collections = Collection.objects.filter(user=request.user)
    context = {
        'collections': collections
    }
    return render(request, 'collections_app/collectionslist.html', context)

# Create collection view
@login_required
def create_collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.image = random.choice(COLLECTION_IMAGES)
            collection.save()
            return redirect('collections_app:empty_collection', collection_id=collection.id)
    else:
        form = CollectionForm()

    return render(request, 'collections_app/collectioncreation.html', {'form': form})

# Empty collection view
@login_required
def empty_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    return render(request, 'collections_app/emptycollection.html', {'collection': collection})

def extract_friendly_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain = domain.replace('www.', '')
    friendly_name = domain.split('.')[0]
    return friendly_name.capitalize()

@login_required
def add_link(request, collection_id=None):
    collections = Collection.objects.filter(user=request.user)
    last_used_collection = Link.objects.filter(collection__user=request.user).order_by('-created_at').first()
    
    collection = None
    show_dropdown = True
    
    if collection_id:
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        show_dropdown = False
    elif last_used_collection:
        collection = last_used_collection.collection
    elif collections.exists():
        collection = collections.first()

    if request.method == 'POST':
        form = LinkForm(request.POST, user=request.user)
        if form.is_valid():
            link = form.save(commit=False)
            link.collection = form.cleaned_data.get('collection') or collection
            
            metadata_url = form.cleaned_data.get('url')
            metadata = fetch_metadata_for_add_link(metadata_url)
            
            if not form.cleaned_data.get('name'):
                if metadata and metadata.get('title'):
                    link.name = metadata['title']
                else:
                    link.name = extract_friendly_name(metadata_url)
            else:
                link.name = form.cleaned_data.get('name')

            link.save()
            return redirect('collections_app:collection_details', collection_id=link.collection.id)
    else:
        form = LinkForm(initial={'collection': collection}, user=request.user)

    context = {
        'form': form,
        'show_dropdown': show_dropdown,
        'selected_collection': collection,
        'collections': collections,
    }
    return render(request, 'collections_app/addlink.html', context)


# Collection Details with Pagination for Infinite Scroll
@login_required
def collection_details(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    links = collection.links.all()

    search_query = request.GET.get('search', '').strip()
    if search_query:
        links = links.filter(
            Q(name__icontains=search_query) |
            Q(url__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    links = links.order_by('-created_at')

    paginator = Paginator(links, 100)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        links_data = [{
            'id': link.id,
            'name': link.name,
            'description': link.description,
            'url': link.url,
            'favicon_url': link.get_favicon_url()
        } for link in page_obj]
        return JsonResponse({
            'links': links_data,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'total_links': links.count()
        })

    return render(request, 'collections_app/collectiondetails.html', {
        'collection': collection,
        'links': [],  # Send an empty list for initial load
        'total_links': links.count()
    })

# Open Collection View
@login_required
def open_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if collection.links.count() > 0:
        return redirect('collections_app:collection_details', collection_id=collection_id)
    else:
        return redirect('collections_app:empty_collection', collection_id=collection_id)

# Delete Collection
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    if request.method == 'GET':
        collection.delete()
        messages.success(request, 'Collection deleted successfully!')
    
    return redirect('collections_app:collections_list')

# Metadata Fetching View (Improved)
def fetch_metadata_for_add_link(url):
    metadata = {}
    
    if url:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract the title (with fallback to domain if no title is found)
                title = soup.title.string.strip() if soup.title else urlparse(url).netloc
                metadata['title'] = title if title else 'No title'

                # Always use Google's favicon service
                parsed_url = urlparse(url)
                metadata['favicon'] = f'https://www.google.com/s2/favicons?sz=64&domain={parsed_url.netloc}'
            else:
                return None
        except requests.RequestException as e:
            return None
    
    return metadata

# def fetch_metadata_for_add_link(url):
#     metadata = {}
    
#     if url:
#         try:
#             response = requests.get(url, timeout=5)
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Extract the title (with fallback to domain if no title is found)
#                 title = soup.title.string.strip() if soup.title else urlparse(url).netloc
#                 metadata['title'] = title if title else 'No title'
                
#                 # Remove favicon fetching - we'll only use Google's service
                
#             else:
#                 return None
#         except requests.RequestException as e:
#             return None
    
    # return metadata


# Delete Link
@require_POST
@login_required
def delete_link(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    link.delete()
    return JsonResponse({'status': 'success'})

@login_required
def get_collection_links(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    links = collection.links.all().values_list('url', flat=True)
    return JsonResponse({'links': list(links)})

@login_required
def fetch_metadata(request):
    url = request.GET.get('url')
    metadata = fetch_metadata_for_add_link(url)
    return JsonResponse(metadata if metadata else {})