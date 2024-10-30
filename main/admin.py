from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Collection, Link

# Customize the User admin interface (optional)
class UserAdmin(BaseUserAdmin):
    model = User
    # Customize the list display or other aspects if needed
    # For example, to show more fields in the list view:
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

# Unregister the default User admin and register it with customizations
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')  # Allows search by name and username

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'collection', 'name', 'created_at')
    search_fields = ('url', 'name', 'collection__name')  # Allows search by URL, name, and collection name
    list_filter = ('collection',)  # Filter links by collection
