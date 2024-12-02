from django.db import models
from django.utils import timezone
from author.models import Author
from django.db.models import Max
from django.utils.text import slugify
import os

class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    CONTENT_TYPE_CHOICES = [
        ('text/markdown', 'Markdown'), 
        ('text/plain', 'UTF-8'),
        ('image/jpeg', 'jpeg'),
        ('application/base64', 'jpeg/png'),
        ('image/png;base64', 'png'),
        ('image/jpeg;base64', 'jpeg'),
        ]
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(blank=True, null=True)
    VISIBILITY_CHOICES = [ # database value/ human readable 
        ('public', 'PUBLIC'),
        ('friends', 'FRIENDS'),
        ('unlisted', 'UNLISTED'),
        ('deleted', 'DELETED')
    ]
    visibility = models.CharField(max_length=11, choices=VISIBILITY_CHOICES, default='public')
    '''
    # From https://stackoverflow.com/questions/58144230/how-to-set-image-field-as-optional by govind
    image_content = models.ImageField(upload_to="post_pics", blank=True, null=True)
    '''
    # READ ONLY
    type = models.CharField(max_length=10, default="post", editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    fqid = models.URLField(blank=True, null=True, max_length=500)
    serial = models.PositiveIntegerField(default=0)
    github_event_id = models.CharField(max_length=500, unique=True, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
        
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.visibility == 'deleted':
                self.is_deleted = True
            # for serial increament
            if self.author.user is not None:
                self.serial = self.author.post_count + 1
                self.author.post_count = self.serial
                self.author.save(update_fields=['post_count']) 
                # for fqid
                self.fqid = self.author.fqid + "/posts/" + str(self.serial)
                if 'image' in self.content_type and self.content:
                    self.image_url = self.fqid + "/image"
        else:
            self.updated_at = timezone.now()
            if self.visibility == 'deleted':
                self.is_deleted = True
            
            
        super(Post, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.author.display_name}:  {self.title}"
    
    @property
    def visibility_display(self):
        """
        Return the human-readable visibility value in uppercase.
        """
        return dict(self.VISIBILITY_CHOICES).get(self.visibility, self.visibility).upper()
    
'''
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
'''

