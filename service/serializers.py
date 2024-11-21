from rest_framework import serializers
from .models import Follow
from author.serializers import Author
from django.contrib.auth.models import User


class SignUpSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(max_length=20, write_only=True)
    bio = serializers.CharField(allow_blank=True, allow_null=True, required=False, write_only=True)
    github_url = serializers.URLField(allow_blank=True, allow_null=True, required=False, write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'display_name', 'bio', 'github_url']
        
    def validate_username(self, value):
        """Ensure the username is unique in the User model."""
        if not value.strip():
            raise serializers.ValidationError("Username is required.")
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value
    
    def validate_password(self, value):
        """TODO: Ensure the password meets the requirements."""
        if not value.strip():
            raise serializers.ValidationError("Password is required.")
        return value
    
    def create(self, validated_data):
        """Create a user first, then create author, author object return as data."""
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(username=username, password=password)
        # User is inactive until approved by the admin
        user.is_active = False
        user.save()
    
        host = self.context.get('host', 'http://test') + 'api/'
        fqid = f'{host}authors/{user.id}'
        author = Author.objects.create(user=user, 
                                       host=host,
                                       fqid=fqid,
                                       **validated_data)
        return author

        
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"
        
