from django.db import models
from django.utils import timezone
from author.models import Author

class ImagePost(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='image_posts')
    title = models.CharField(max_length=255)
    image_content = models.TextField(blank=True, null=True)      # Storing the image as base64-encoded data
    content_type = models.TextField(default="image/jpeg") 
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friend-only', 'Friend Only'),
        ('unlisted', 'Unlisted'),
    ]
    visibility = models.CharField(max_length=11, choices=VISIBILITY_CHOICES, default='public')
    
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title