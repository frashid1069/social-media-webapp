from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.


class Author(models.Model):
     # Link to Django's User model
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=20, unique=True)
    bio = models.TextField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    # From https://www.devhandbook.com/django/user-profile/
    profile_image = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    #email = models.EmailField(unique=True)
    
    def __str__(self):
        return str(self.id)