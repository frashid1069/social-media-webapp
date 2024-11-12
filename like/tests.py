from django.test import TestCase
from service.tests import BaseAPITestCase
from rest_framework import status
from like.models import Post, Like
from django.urls import reverse

class LikeViewTest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        # Create a sample post for testing likes
        self.post = Post.objects.create(author=self.author1, title="Test Post", content="This is a test post.")
        # Define the URL for creating a like, so it can be used across tests
        self.like_url = reverse("like-list")

    def test_create_like(self):
        """
        Tests that a like can be created for a post by an author.
        """
        data = {
            "author": self.author1.id,
            "post": self.post.id
        }
        response = self.client.post(self.like_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(response.data["author"], self.author1.id)
        self.assertEqual(response.data["post"], self.post.id)

    def test_create_duplicate_like(self):
        """
        Tests that creating a duplicate like does not create a new entry.
        """
        # First like creation
        data = {
            "author": self.author1.id,
            "post": self.post.id
        }

        # Attempt to create a duplicate like
        response = self.client.post(self.like_url, data, format="json")
        self.assertEqual(Like.objects.count(), 1)   # only one like object should still remain
