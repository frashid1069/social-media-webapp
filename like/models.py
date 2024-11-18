from django.db import models
from datetime import datetime
from author.models import Author
from post.models import Post


class Like(models.Model):    
    # READ ONLY
    type = models.CharField(max_length=10, default="like", editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='likes')
    object = models.URLField(blank=True, null=True, max_length=200)
    fqid = models.URLField(blank=True, null=True, max_length=200, unique=True)
    serial = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.now)
    
    def __str__(self):
        return f"Like by {self.author} on {self.post}"
    
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            # for serial increament
            self.serial = self.author.like_count + 1
            self.author.like_count = self.serial
            self.author.save(update_fields=['like_count']) 
            # for fqid
            self.fqid = self.author.fqid + "/liked/" + str(self.serial)
        super().save(*args, **kwargs)
    
