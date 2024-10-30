# main/models.py

from django.db import models
from django.contrib.auth.models import User

class Collection(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections_from_main')  # Add related_name here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Link(models.Model):
    url = models.URLField()
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
