from rest_framework import serializers
from .models import ImagePost

class ImagePostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ImagePost
        exclude = ['created_at', 'updated_at', 'is_deleted', 'image_url']
        
    def create(self, validated_data):
        # Create the image post instance
        image_post = ImagePost.objects.create(**validated_data)

        # Generate the display URL based on the new image ID and author ID
        request = self.context.get('request')
        author_serial = image_post.author.id
        image_url = request.build_absolute_uri(f'/api/image_post/image/?author_id={author_serial}&image_id={image_post.id}')

        # Save the URL in the `image_url` field
        image_post.image_url = image_url
        image_post.save()

        return image_post
        