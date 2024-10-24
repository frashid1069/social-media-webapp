from django.db import models
from datetime import datetime
from django.utils.text import slugify
import os
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
     # Link to Django's User model
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=50, default='1')
    bio = models.TextField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    # From https://www.devhandbook.com/django/user-profile/
    profile_image = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    #email = models.EmailField(unique=True)
    
    def __str__(self):
        return str(self.id)
    
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

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True) 
    content_type = models.CharField(max_length=50, choices=[('text/markdown', 'Markdown'), ('image/jpeg', 'JPEG')])
    # From https://stackoverflow.com/questions/58144230/how-to-set-image-field-as-optional by govind
    image_content = models.ImageField(upload_to="post_pics", blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    # database value/ human readable 
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friend-only', 'Friend Only'),
        ('unlisted', 'Unlisted'),
    ]
    visibility = models.CharField(max_length=11, choices=VISIBILITY_CHOICES, default='public')
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class Like(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Like by {self.author} on {self.post}"

class Follow(models.Model):
    '''Follower.objects.create(follower=author1, followed=author2) 
    => author1 follows author2
    authors_followed_by_author1 = author1.following.all() Returns [author2]
    followers_of_author2 = author2.followers.all()  # Returns [author1]'''
    
    # related_name='following' allows you to get all the authors that a particular author is following.
    follower = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='following')
    
    # related_name='followers' allows you to get all the users who follow a particular Author via this ForeignKey
    followed = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followers')
    
    PENDING_CHOICES = [('yes', 'Yes'), ('no', 'No')]
    pending = models.CharField(max_length=10, choices=PENDING_CHOICES, default='yes')
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.follower} follows {self.followed}"
    
    def get_follower(self):
        return self.follower
    

# Inbox Model
class Inbox(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='inbox')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    like = models.ForeignKey(Like, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Inbox for {self.author}"