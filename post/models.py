from django.db import models
from django.utils import timezone
from author.models import Author
from django.utils.text import slugify
import os

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True) 
    content_type = models.CharField(max_length=50, choices=[('text/markdown', 'Markdown'), ('image/jpeg', 'JPEG')])
    
    # From https://stackoverflow.com/questions/58144230/how-to-set-image-field-as-optional by govind
    image_content = models.ImageField(upload_to="post_pics", blank=True, null=True)
    # database value/ human readable 
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friend-only', 'Friend Only'),
        ('unlisted', 'Unlisted'),
    ]
    visibility = models.CharField(max_length=11, choices=VISIBILITY_CHOICES, default='public')
    
    github_event_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

def upload_post_image(instance, filename):
    # - sukh 
    # This function is used to define the file path for uploading an image for a post.
    # It renames the file using a slugified version of the post's title and places it in the "post_pics/" directory.

    # Split the original filename into the base (name) and extension (file type).
    # Example: If the filename is "image.jpg", base = "image" and ext = ".jpg"
    base, ext = os.path.splitext(filename)

    # Slugify the title of the post.
    # This means converting the post title (instance.title) into a URL-friendly format.
    # Example: If the post title is "My First Post!", slugify(instance.title) will return "my-first-post".
    slugified_title = slugify(instance.title)  # slugify is useful for making readable, URL-safe filenames.

    # Create the new filename by combining the slugified title and the original file extension.
    # Example: If slugified_title = "my-first-post" and ext = ".jpg", new_filename will be "my-first-post.jpg".
    new_filename = f"{slugified_title}{ext}"

    # Return the full path where the file will be stored. The file will be placed inside the "post_pics/" directory.
    # os.path.join("post_pics", new_filename) will create a path like "post_pics/my-first-post.jpg".
    return os.path.join("post_pics", new_filename)



# Repost Model
class Repost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reposts')
    reposted_by = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='reposts')
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    visibility = models.CharField(max_length=20, choices=[('public', 'Public'), ('unlisted', 'Unlisted'), ('friend-only', 'Friend Only')], default='public')
    
    def __str__(self):
        return f"{self.post} reposted {self.reposted_by}"