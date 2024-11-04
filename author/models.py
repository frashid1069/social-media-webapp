from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.


class Author(models.Model):
     # Link to Django's User model
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=20, unique=True)
    bio = models.TextField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True, max_length=200, unique=True)
    # From https://www.devhandbook.com/django/user-profile/
    profile_image = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    #email = models.EmailField(unique=True)

    
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
