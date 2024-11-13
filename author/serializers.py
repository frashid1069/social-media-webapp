from datetime import timezone
from rest_framework import serializers
from .models import Author


class AuthorSerializer(serializers.ModelSerializer):
    # type = serializers.CharField(default="author", read_only=True)
    id = serializers.URLField(source="fqid", read_only=True)
    displayName = serializers.CharField(source="display_name")
    github = serializers.URLField(source="github_url")
    profileImage = serializers.URLField(source="profile_image", required=False)
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
        
    def create(self, validated_data):
        author = Author.objects.create(**validated_data)
        request = self.context.get('request')
        if request:
            fqid = request.build_absolute_uri(f'/api/authors/{author.serial}')
            author.fqid = fqid
            author.save()  

        return author

        

