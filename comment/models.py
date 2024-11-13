from django.db import models
from datetime import datetime
from author.models import Author
from post.models import Post

class Comment(models.Model):
    content = models.TextField()
    content_type = models.CharField(max_length=50, default='text/markdown')
    
    # READ ONLY
    type = models.CharField(max_length=10, default="comment", editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    fqid = models.URLField(blank=True, null=True, max_length=200, unique=True)
    serial = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    is_deleted = models.BooleanField(default=False)
     
    def save(self, *args, **kwargs):
        if self._state.adding:
            # for serial increament
            self.serial = self.post.comment_count + 1
            self.post.comment_count = self.serial
            self.post.save(update_fields=['comment_count']) 
            # for fqid
            self.fqid = self.author.fqid + "/commented/" + str(self.serial)
        
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
