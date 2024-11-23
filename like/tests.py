from django.test import TestCase
from service.tests import BaseAPITestCase
from rest_framework import status
from like.serializers import Like
from post.serializers import Post
from comment.serializer import Comment
from author.serializers import AuthorSerializer
from django.urls import reverse
from author.models import Author
from author.serializers import AuthorSerializer

class LikeViewTest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
    
    # ://service/api/authors/{AUTHOR_SERIAL}/inbox
    def test_post_like(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        data = {
            "type":"like",
            "author":serializer.data,
            "object":post.fqid 
        }
        response = self.client.post(reverse('inbox', args=[1]), data, format="json")
        likes = Like.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(likes), 1)
    
    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/likes
    def test_get_post_likes(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        like = Like.objects.create(author=author1, object=post.fqid)
        response = self.client.get(reverse('liked_post', args=[1, 1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/posts/{POST_FQID}/likes 
    def test_get_post_fqid_likes(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        like = Like.objects.create(author=author1, object=post.fqid)
        response = self.client.get(reverse('fqid_liked_post', args=[post.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments/{COMMENT_FQID}/likes 
    def test_get_comment_likes(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="Sick Olde English", post=post)
        like = Like.objects.create(author=author1, object=comment.fqid)
        response = self.client.get(reverse('liked_comment', args=[1, 1, comment.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], comment.fqid+"/likes")

    # ://service/api/authors/{AUTHOR_SERIAL}/liked 
    def test_get_author_liked(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        like = Like.objects.create(author=author1, object=post.fqid)
        response = self.client.get(reverse('things_liked_by_author', args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL} 
    def test_get_single_like(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        like = Like.objects.create(author=author1, object=post.fqid)
        response = self.client.get(reverse('like_detail', args=[1, 1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
     # ://service/api/authors/{AUTHOR_FQID}/liked
    def test_get_fqid_author_liked(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        like = Like.objects.create(author=author1, object=post.fqid)
        response = self.client.get(reverse('things_liked_by_author_fqid', args=[author1.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/liked/{LIKE_FQID}
    def test_get_liked_fqid(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        like = Like.objects.create(author=author1, object=post.fqid)
        response = self.client.get(reverse('fqid_like_detail', args=[like.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)