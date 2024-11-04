from datetime import timezone
from rest_framework import serializers
from .models import Author


class AuthorSerializer(serializers.ModelSerializer):
    # type = serializers.CharField(default="author", read_only=True)
    id = serializers.URLField(source="fqid", read_only=True)
    displayName = serializers.CharField(source="display_name")
    github = serializers.URLField(source="github_url")
    profileImage = serializers.URLField(source="profile_image", required=False)
    
    class Meta:
        model = Author
        fields = [
            "type",
            "id",
            "host",
            "displayName",
            "github",
            "profileImage",
        ]
        #read_only_fields = ['user', 'id', 'created_at', 'updated_at']
