from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.


class Author(models.Model):
    display_name = models.CharField(max_length=50)
    bio = models.TextField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True, max_length=500)
    profile_image = models.URLField(blank=True, null=True, max_length=500, default="") # From https://www.devhandbook.com/django/user-profile/
    
    # READ ONLY
    type = models.CharField(max_length=10, default="author", editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True) # Link to Django's User model
    serial = models.PositiveIntegerField(default=0)
    fqid = models.URLField(blank=True, null=True, max_length=500, unique=True)
    host = models.URLField(blank=True, null=True, max_length=500)
    post_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            
            if self.user:
                self.serial = self.user.id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name  # Simpler __str__ for clarity
    
    def is_friend_with(self, other_author):
        """
        Determines if the current author has a mutual friendship with another author.
        
        This function checks for a "friend" relationship by verifying that both authors follow each other
        with non-pending follow requests (i.e., 'pending' status is set to 'no'). For two authors to be 
        considered friends, both must have approved follow requests in each other's direction.

        Args:
            other_author (Author): The other author to check for mutual friendship.

        Returns:
            bool: True if there is a mutual friendship (i.e., both authors follow each other without 
                pending requests), otherwise False.
                
        Note:
            - Uses the Follow model to check for follow records where each author follows the other 
            with 'pending' set to 'no'.
            - This helps maintain the integrity of friendships, as only mutual, approved follows qualify.
        """
        from service.models import Follow
        """Check if the current author and the specified author are friends (mutual follows)."""
        return Follow.objects.filter(follower=self, followed=other_author, pending='no').exists() and \
               Follow.objects.filter(follower=other_author, followed=self, pending='no').exists()
