from service.tests import BaseAPITestCase
from django.urls import reverse
from rest_framework import status
import base64
from io import BytesIO
from PIL import Image
from .models import Post
from author.models import Author
from django.contrib.auth.models import User
from service.models import Follow
from author.serializers import AuthorSerializer

class PostViewTest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
    
    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL} Get
    def test_get_post(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "PUBLIC")
        response = self.client.get(reverse("post_detail", args=[1,1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Post 1")

    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL} Delete
    def test_delete_post(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "PUBLIC")
        response = self.client.delete(reverse("post_detail", args=[1,1]))
        post.refresh_from_db()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(post.is_deleted, True)

    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL} Put
    def test_put_post(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "PUBLIC")
        data = {"author":author1.fqid, "title":"Updated title"}
        response = self.client.put(reverse("post_detail", args=[1,1]), data, format="json")
        post = Post.objects.get(id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.title, "Updated title")
    
    # ://service/api/posts/{POST_FQID} public
    def test_get_public_post(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "PUBLIC")
        post = Post.objects.get(id=1)
        response = self.client.get(reverse("fqid_post_detail", args=[post.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Post 1")

    # ://service/api/posts/{POST_FQID} friends-only
    def test_get_friends_only_post(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author2 = self.client.get(reverse('author-detail', args=[2]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        author2 = Author.objects.get(fqid=author2.data["id"])
        post = Post.objects.create(author=author2, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "FRIENDS")
        Follow.objects.create(follower=author2, followed=author1, pending="no")
        Follow.objects.create(follower=author1, followed=author2, pending="no")
        author1.refresh_from_db()
        author2.refresh_from_db()
        post.refresh_from_db()
        response = self.client.get(reverse("fqid_post_detail", args=[post.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Post 1")

    # ://service/api/authors/{AUTHOR_SERIAL}/posts/ Get
    def test_get_authors_posts(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "FRIENDS")
        Post.objects.create(author=author1, title="Test Post 2", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "PUBLIC")
        response = self.client.get(reverse("post_list", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    # ://service/api/authors/{AUTHOR_SERIAL}/posts/ Post 
    def test_post_author_post(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        data = {"author": serializer.data, "title":"Test Post 1", "description":"This is a test post", "contentType":"text/markdown", "content":"Content of the post", "visibility":"PUBLIC"}
        response = self.client.post(reverse("post_list", args=[1]), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(author=author1)
        self.assertEqual(post.title, "Test Post 1")
        
    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/image
    def test_get_image_post(self):    
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"]) 
        image = BytesIO()
        Image.new("RGB", (100, 100), color="red").save(image, format="JPEG")
        image.seek(0)  # Reset file pointer to start
        image_content = base64.b64encode(image.getvalue()).decode("utf-8")
        Post.objects.create(
            title="Image Title",
            author= author1,
            content= image_content,
            content_type= "image/jpeg;base64",
            visibility="PUBLIC",
            is_deleted=False
        )
        response = self.client.get(reverse("post_image", args=[1, 1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # ://service/api/posts/{POST_FQID}/image
    def test_get_image_fqid_post(self):    
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"]) 
        image = BytesIO()
        Image.new("RGB", (100, 100), color="red").save(image, format="JPEG")
        image.seek(0)  # Reset file pointer to start
        image_content = base64.b64encode(image.getvalue()).decode("utf-8")
        post = Post.objects.create(
            author=author1, 
            title="Image Title", 
            description = "This is an image post", 
            content_type = "image/jpeg", 
            content = image_content, 
            visibility = "PUBLIC")
        post.save()
        post1 = Post.objects.get()
        response = self.client.get(reverse("fqid_post_image", args=[post.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)



