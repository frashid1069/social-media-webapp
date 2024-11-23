from django.urls import reverse
from service.tests import BaseAPITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Comment, Post
from author.serializers import AuthorSerializer
from author.models import Author

class CommentViewTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()

    # ://service/api/authors/{AUTHOR_SERIAL}/inbox
    def test_post_comment(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        data = {
            "type":"comment",
            "author":author1.fqid,
            "comment":"Sick Olde English",
            "contentType":"text/markdown", 
            "post":post.fqid 
        }
        response = self.client.post(reverse('inbox', args=[1]), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
    def test_get_comments(self):
        self.test_post_comment()
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        response = self.client.get(reverse('comment_list', args=[1,1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/posts/{POST_FQID}/comments 
    def test_get_fqid_comments(self):
        self.test_post_comment()
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.get(title="Test Post 1")
        response = self.client.get(reverse('fqid_comment_list', args=[post.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
    
    # ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID} 
    def test_get_remote_comments(self):
        self.test_post_comment()
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.get(title="Test Post 1")
        comment = Comment.objects.get(post=post.id)
        response = self.client.get(reverse('comment-detail', args=[1, 1, comment.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "http://test/api/1/commented/1")
    
    # ://service/api/authors/{AUTHOR_SERIAL}/commented Get 
    def test_get_commented(self):
        self.test_post_comment()
        response = self.client.get(reverse('author_comment_list', args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    # ://service/api/authors/{AUTHOR_SERIAL}/commented Post 
    def test_post_commented(self):
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        serializer = AuthorSerializer(author1)
        post = Post.objects.create(author=author1, title="Test Post 1", description = "This is a test post", content_type = "text/markdown", content = "Content of the post", visibility = "public")
        data = {
            "type":"comment",
            "author":author1.fqid,
            "content":"Sick Olde English",
            "contentType":"text/markdown", 
            "post":post.fqid 
        }
        response = self.client.post(reverse('author_comment_list', args=[1]), data, format="json")
        comments = Comment.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(comments), 1)
    
    # ://service/api/authors/{AUTHOR_FQID}/commented 
    def test_fqid_commented(self):
        self.test_post_comment()
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        response = self.client.get(reverse('fqid_author_comment_list', args=[author1.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    # ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
    def test_get_commented_comment(self):
        self.test_post_comment()
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.get(title="Test Post 1")
        comment = Comment.objects.get(post=post.id)
        response = self.client.get(reverse('comment_detail', args=[1, 1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "http://test/api/1/commented/1")
    
    # ://service/api/commented/{COMMENT_FQID} 
    def test_get_fqid_commented_comment(self):
        self.test_post_comment()
        author1 = self.client.get(reverse('author-detail', args=[1]))
        author1 = Author.objects.get(fqid=author1.data["id"])
        post = Post.objects.get(title="Test Post 1")
        comment = Comment.objects.get(post=post.id)
        response = self.client.get(reverse('fqid_comment_detail', args=[comment.fqid]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], "http://test/api/1/commented/1")