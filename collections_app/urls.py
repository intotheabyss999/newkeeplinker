from django.urls import path
from .views import create_collection
from . import views

app_name = 'collections_app'

urlpatterns = [
    path('create/', views.create_collection, name='create_collection'),
    path('<int:collection_id>/', views.collection_details, name='collection_details'),
    path('list/', views.collections_list, name='collections_list'),
    path('empty/<int:collection_id>/', views.empty_collection, name='empty_collection'),
    path('collection/<int:collection_id>/add_link/', views.add_link, name='add_link'),
    path('open/<int:collection_id>/', views.open_collection, name='open_collection'),
    path('delete/<int:collection_id>/', views.delete_collection, name='delete_collection'),
    path('collection/<int:collection_id>/add_link/', views.add_link, name='add_link'),
    path('fetch_metadata/', views.fetch_metadata, name='fetch_metadata'),
    path('delete_link/<int:link_id>/', views.delete_link, name='delete_link'),
    path('get_collection_links/<int:collection_id>/', views.get_collection_links, name='get_collection_links'),
    path('add-link/', views.add_link, name='add_link'),
    path('add-link/<int:collection_id>/', views.add_link, name='add_link_with_collection'),
    path('fetch_metadata/', views.fetch_metadata_for_add_link, name='fetch_metadata'),
]
