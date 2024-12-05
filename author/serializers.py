from datetime import timezone
from rest_framework import serializers
from .models import Author



class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.URLField(source="fqid", required=True)
    host = serializers.URLField(required=True)
    displayName = serializers.CharField(source="display_name", required=True)
    github = serializers.URLField(source="github_url", required=False, allow_null=True, allow_blank=True)
    profileImage = serializers.URLField(source="profile_image", read_only=True, allow_null=True, allow_blank=True)
    page = serializers.URLField(source='fqid', read_only=True)
    
    class Meta:
        model = Author
        fields = [
            "type",
            "id",
            "host",
            "displayName",
            "github",
            "profileImage",
            "page"
        ]
        
    def validate_host(self, value):
        """
        Ensure the host ends with '/api/' and normalize its format.
        """
        value = value.rstrip("/")  # Remove trailing slashes
        
        # Ensure '/api/' is at the end
        if not value.endswith("/api"):
            value += "/api"
        
        # Add a trailing slash
        value += "/"
        
        if not (value.startswith("http://") or value.startswith("https://")):
            raise serializers.ValidationError("Host must include a valid protocol (http:// or https://).")
        
        return value
        
    def validate_id(self, value):
        """
        Ensure the id (fqid) is unique in the database.
        """
        value = value.rstrip("/")  # Normalize the id to avoid trailing slash issues
        if Author.objects.filter(fqid=value).exists():
            raise serializers.ValidationError("An author with this id already exists.")
        return value


