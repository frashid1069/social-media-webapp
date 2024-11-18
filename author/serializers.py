from datetime import timezone
from rest_framework import serializers
from .models import Author



class AuthorSerializer(serializers.ModelSerializer):
    id = serializers.URLField(source="fqid", required=True)
    host = serializers.URLField(required=True)
    displayName = serializers.CharField(source="display_name", required=True)
    github = serializers.URLField(source="github_url", required=False, allow_null=True, allow_blank=True)
    profileImage = serializers.URLField(source="profile_image", required=False, allow_null=True, allow_blank=True)
    page = serializers.URLField(source='fqid', required=True)
    
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
        

        

