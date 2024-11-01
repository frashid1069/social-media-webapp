from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ImagePost
import base64
from io import BytesIO
from PIL import Image

class ImagePostTests(APITestCase):

    def setUp(self):
        self.image = BytesIO()
        Image.new("RGB", (100, 100), color="red").save(self.image, format="JPEG")
        self.image.seek(0)  # Reset file pointer to start

        # Endpoints for testing
        self.create_url = reverse("imagepost-list")  # URL for creating image posts
        self.retrieve_url_template = "imagepost-detail"  # Template for retrieving image posts

    # POST request tests
    def test_create_image_post_success(self):
            """Test creating an image post successfully."""
            response = self.client.post(
                self.create_url,
                {
                    "author_id": 1,
                    "post_id": 1,
                    "image_content": self.image,  # Upload image as file
                },
                format="multipart"  # Important for handling file uploads
            )

            # Ensure the image post is created successfully
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("base64_data", response.data)  # Verify base64 data is in the response

    def test_create_image_post_no_file(self):
        """Test creating an image post without providing an image file."""
        response = self.client.post(
            self.create_url,
            {
                "author_id": 1,
                "post_id": 1,
                # No image_content field provided
            },
            format="multipart"
        )

        # Expect a 400 Bad Request due to missing file
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "An image file is required.")
    
    # GET request tests
    def test_retrieve_image_post_success(self):
        """Test retrieving an existing image post as binary data."""
        # First, create an image post entry directly in the database
        image_post = ImagePost.objects.create(
            author_id=1,
            post_id=1,
            base64_data="data:image/jpeg;base64," + base64.b64encode(self.image.getvalue()).decode("utf-8"),
        )

        # Use the detail URL for retrieving a single post
        retrieve_url = reverse(self.retrieve_url_template, args=[image_post.id])
        response = self.client.get(retrieve_url)

        # Ensure the retrieval was successful and returns image data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "image/jpeg")  # Content-Type based on the image MIME type

    def test_retrieve_image_post_not_found(self):
        """Test retrieving a non-existent image post, expecting a 404 error."""
        # Try retrieving an image post with a non-existent ID
        retrieve_url = reverse(self.retrieve_url_template, args=[9999])  # Non-existent ID
        response = self.client.get(retrieve_url)

        # Expect a 404 Not Found response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)