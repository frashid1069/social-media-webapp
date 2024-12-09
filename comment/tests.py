from django.urls import reverse
from service.tests import BaseAPITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Comment, Post
from author.serializers import AuthorSerializer
from author.models import Author
from post.serializers import PostSerializer 

class CommentViewTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
    
    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
    def test_get_comments(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="new comment", post=post.fqid)
        response = self.client.get(reverse('comment_list', args=[1,1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/posts/{POST_FQID}/comments 
    def test_get_fqid_comments(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="new comment", post=post.fqid)
        response = self.client.get(reverse('fqid_comment_list', kwargs={"POST_FQID":post.fqid}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID} 
    def test_get_remote_comments(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="new comment", post=post.fqid)
        response = self.client.get(reverse('comment-detail', args=[1, 1, comment.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "http://127.0.0.1:8000/api/authors/1/commented/1")
    
    # ://service/api/authors/{AUTHOR_SERIAL}/commented Get 
    def test_get_commented(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="new comment", post=post.fqid)
        response = self.client.get(reverse('author_comment_list', args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    # ://service/api/authors/{AUTHOR_SERIAL}/commented Post 
    # ://service/api/authors/{AUTHOR_SERIAL}/inbox
    def test_post_commented(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        data = {"author": serializer.data, "title":"Test Post 1", "description":"This is a test post", "contentType":"text/markdown", "content":"Content of the post", "visibility":"PUBLIC"}
        post_serializer = PostSerializer(data=data)
        if post_serializer.is_valid():
            post_serializer.save(author=author1)
        new_post = Post.objects.get(title="Test Post 1")
        data = {
            "type":"comment",
            "author":serializer.data,
            "comment":"Sick Olde English",
            "contentType":"text/markdown", 
            "post":new_post.fqid
        }
        response = self.client.post(reverse('author_comment_list', args=[1]), data, format="json")
        comments = Comment.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    # ://service/api/authors/{AUTHOR_FQID}/commented 
    def test_fqid_commented(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="new comment", post=post.fqid)
        response = self.client.get(reverse('fqid_author_comment_list', args=[author1.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    # ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
    def test_get_commented_comment(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="new comment", post=post.fqid)
        response = self.client.get(reverse('comment_detail', args=[1, 1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "http://127.0.0.1:8000/api/authors/1/commented/1")
    
    # ://service/api/commented/{COMMENT_FQID} 
    def test_get_fqid_commented_comment(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        comment = Comment.objects.create(author=author1, content="new comment", post=post.fqid)
        response = self.client.get(reverse('fqid_comment_detail', args=[comment.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "http://127.0.0.1:8000/api/authors/1/commented/1")