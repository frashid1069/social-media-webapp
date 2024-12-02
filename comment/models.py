from django.db import models
from django.utils import timezone
from author.models import Author
from post.models import Post

class Comment(models.Model):
    content = models.TextField()
    content_type = models.CharField(max_length=50, default='text/markdown')
    
    # READ ONLY
    type = models.CharField(max_length=10, default="comment", editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comments')
    post = models.URLField(blank=True, null=True, max_length=500)
    fqid = models.URLField(blank=True, null=True, max_length=500, unique=True)
    serial = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
     
    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.author.user is not None:
                # for serial increament
                self.serial = self.author.comment_count + 1
                self.author.comment_count = self.serial
                self.author.save(update_fields=['comment_count']) 
                # for fqid
                self.fqid = self.author.fqid + "/commented/" + str(self.serial)
        else:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return f"{self.author} comment on '{self.post.title}'"
