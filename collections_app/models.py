from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Collection(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections_from_app')  # Add related_name here
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.CharField(max_length=100)  

    def __str__(self):
        return self.name
    
class Link(models.Model):
    collection = models.ForeignKey(Collection, related_name='links', on_delete=models.CASCADE)
    url = models.URLField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_favicon_url(self):
        # Extract the domain from the URL and use Google's favicon service
        domain = self.url.split('/')[2]  # Assuming the URL starts with http:// or https://
        return f"https://www.google.com/s2/favicons?sz=64&domain={domain}"

    def __str__(self):
        return self.name