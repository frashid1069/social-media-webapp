from service.tests import BaseAPITestCase
from django.urls import reverse
from rest_framework import status
import base64
from io import BytesIO
from PIL import Image
from .models import Post, Repost

class PostViewTest(BaseAPITestCase):
    '''        data = {
            'title': 'New Post',
            'author': self.author.id,
            'content': 'New content',
            "content_type": "text/markdown",
            'visibility': 'public'
        }'''
    def setUp(self):
        super().setUp()
        # Create a user and an author
        self.post = Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)
        
        # Create an image
        self.image = BytesIO()
        Image.new("RGB", (100, 100), color="red").save(self.image, format="JPEG")
        self.image.seek(0)  # Reset file pointer to start
    
        # Endpoints for testing
        self.create_url = reverse("post-list")  # URL for creating image posts
        self.retrieve_url_template = "post-detail"  # Template for retrieving image posts
        
        self.image_post = Post.objects.create(
            title="Image Title",
            author= self.author,
            content= base64.b64encode(self.image.getvalue()).decode("utf-8"),
            content_type= "image/jpeg",
            visibility="public",
            is_deleted=False
        )
        
        
    def test_post_creation(self):
        """
        POST request to '/api/post/'
        Test that a post is created correctly.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Post',
            'author': self.author.user.id,
            'content': 'New content',
            "content_type": "text/markdown",
        }
        response = self.client.post(reverse('post-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')
        
    def test_get_post_list(self):
        """
        GET request to '/api/post/'
        Test getting a list of posts.
        """
        for i in range(2):
            Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_filter_posts_by_author(self):
        """
        GET request to '/api/post/?author_id=<pk>'
        Test filtering posts by author ID.
        """
        for i in range(2):
            Post.objects.create(author=self.author, title="Test Post", visibility="public", is_deleted=False)
            
        response = self.client.get(reverse('post-list'), {'author_id': self.author.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    # POST request tests
    def test_create_image_post_success(self):
        """
        POST request to '/api/image_post/'
        Test creating an image post successfully.
        """
        response = self.client.post(
            self.create_url,
            {
                "title":"Image Title",
                "author": 1,
                "content": self.image,  
                "content_type": "image/jpeg",
                "visibility": "public",
            },
        )
        # Ensure the image post is created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("content", response.data)  # Verify base64 data is in the response
        
    def test_create_image_post_no_file(self):
        """
        POST request to '/api/post/'
        Test creating an image post without providing an image file.
        """
        response = self.client.post(
            self.create_url,
            {
                "author_id": 1,
                "post_id": 1,
                "content_type": "image/jpeg",
                # No content field provided
            },
            format="multipart"
        )

        # Expect a 400 Bad Request due to missing file
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "An image file is required.")
    
    # GET request tests
    def test_retrieve_image_post_success(self):
        """
        GET request to '/api/image_post/1/'
        Test retrieving an existing image post as binary data.
        """
        
        # Use the detail URL for retrieving a single post
        retrieve_url = reverse(self.retrieve_url_template, args=[self.image_post.id])
        response = self.client.get(retrieve_url)

        # Ensure the retrieval was successful and returns image data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("content", response.data)  # Content-Type based on the image MIME type

    def test_retrieve_image_post_not_found(self):
        """
        GET request to '/api/post/1/'
        Test retrieving a non-existent image post, expecting a 404 error.
        """
        # Try retrieving an image post with a non-existent ID
        retrieve_url = reverse(self.retrieve_url_template, args=[9999])  # Non-existent ID
        response = self.client.get(retrieve_url)

        # Expect a 404 Not Found response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_get_image(self):
        """
        GET request to '/api/image_post/image/?author_id={author_serial}&image_id={image_post.id}'
        Test retrieving an image from image_post api, expecting binary image data.
        """
        # Prepare the URL for the get_image action with author_id and image_id
        url = reverse('post-get_image')  
        params = {'author_id': self.user.id, 'post_id': self.image_post.id}
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Decode the returned image and check if it matches the original
        returned_image_base64 = base64.b64encode(response.content).decode('utf-8')
        original_image_base64 = self.image_post.content
        
        self.assertEqual(returned_image_base64, original_image_base64)

        # Verify content type
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        
    # def test_filter_posts_by_visibility(self):
    #     """
    #     GET request to '/api/post/?author_id=<pk>'
    #     Test filtering posts by author ID.
    #     """
    
    
# Below test cases made with the help of OpenAI. (2023). ChatGPT (GPT-3.5) "how to write test cases for an api in django python" 2024-11-03 
''' Below test cases made with the help of OpenAI. (2023). ChatGPT (GPT-3.5) "how to write to check this repost api:  " 2024-11-03  
    I included the api code for the repost in chatgpt aswell
'''         
class RepostViewTest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(author=self.author1, title="Test Post", visibility="public")
        self.repost_url = reverse('repost-list')

    def test_create_repost_success(self):
        """
        Test successful repost creation.
        """
        data = {
            "post": self.post.id,
            "reposted_by": self.author2.id
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['post'], self.post.id)
        self.assertEqual(response.data['reposted_by'], self.author2.id)

    def test_create_repost_missing_fields(self):
        """
        Test repost creation with missing fields.
        """
        data = {
            "post": self.post.id
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Post and reposted_by fields are required.')

    def test_create_repost_nonexistent_post(self):
        """
        Test repost creation with a non-existent post.
        """
        data = {
            "post": 999,
            "reposted_by": self.author2.id
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_repost_nonexistent_author(self):
        """
        Test repost creation with a non-existent author.
        """
        data = {
            "post": self.post.id,
            "reposted_by": 999
        }
        response = self.client.post(self.repost_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_delete_repost(self):
        """
        Test deleting a repost.
        """
        repost = Repost.objects.create(post=self.post, reposted_by=self.author2)
        delete_url = reverse('repost-detail', args=[repost.id])
        response = self.client.delete(delete_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Repost.objects.filter(id=repost.id).exists())