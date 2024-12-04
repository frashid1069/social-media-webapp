from django.shortcuts import render
import requests 
from django.urls import reverse
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.test.client import RequestFactory
from post.views import post_list
from service.utils.check_friend import check_friend
from post.serializers import Post, PostSerializer
import json
import re
import os
import openai
openai.api_key = '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'


@api_view(['POST'])
def chatgpt_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            key = None
            
            if "make a post" in prompt.lower() or "create a post" in prompt.lower():
                key = 1
                prompt = f"Please provide the following content as a JSON object, and output only the JSON without any extra text:\n{prompt}"
            elif "summarize post" in prompt.lower() or "summarize posts" in prompt.lower():
                key = 2
                data = get_all_posts(request)
                prompt = f"Answer in 3 points of 5 words each to summarize:\n{data}"
                prompt = f"Write a summary using only 20 words. No extra details:\n{data}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the assistant's reply
            reply = response.choices[0].message['content']

            print(reply)
            # Check if the reply is JSON-like for post creation
            if key == 1:
                try:
                    # Use a regular expression to extract the JSON object
                    # json_match = re.search(r'\{.*?\}', reply, re.DOTALL)
                    # if json_match:
                    #     json_str = json_match.group()
                    #     json_str = json_str.replace("'", '"')
                    #     # Escape the newline characters
                    #     json_str_fixed = json_str.replace('\n', '\\n')
                    #     try:
                    #         reply_data = json.loads(json_str_fixed)
                    #         print("Parsed JSON:", reply_data)
                    #     except json.JSONDecodeError as e:
                    #         print("Error decoding JSON:", e)
                    # else:
                    #     print("No JSON object found in the reply")
                    reply_data = json.loads(reply)
                    title = reply_data.get('title', '')
                    content = reply_data.get('content', '')
                    content_type = reply_data.get('contentType', '')
                    if content_type != "text/markdown" or content_type != 'text/plain':
                        content_type = 'text/markdown'
                        
                    
                    factory = RequestFactory()
                    internal_request = factory.post(
                        reverse('post_list', args=[request.user.author.serial]),
                        data={
                            'title': title,
                            'content': content,
                            'description': 'This is a post made by Aqua AI',
                            'contentType': content_type,
                            'visibility': 'PUBLIC'
                        },
                        HTTP_AUTHORIZATION=f'Bearer {request.auth}'
                    )
                    response = post_list(internal_request, AUTHOR_SERIAL=request.user.author.serial)
                    if response.status_code == 201:
                        return JsonResponse({'response': f'I created a post with title: {title}'})
                    else:
                        return JsonResponse({'response': 'Someone tell Rex there is a problem with my AI.'}, status=500)

                except json.JSONDecodeError:
                    return JsonResponse({'response': json.JSONDecodeError})  # Return the original response if parsing fails
            
            elif key == 2:
                print(2)
                return JsonResponse({'response': reply})
            else:
                return JsonResponse({'response': reply})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'response': "Someone tell Rex there is a problem with my AI"}, status=500)

    print({'error': 'Invalid request method'})
    return JsonResponse({'response': 'Someone tell Rex there is a problem with my AI'}, status=405)


def get_all_posts(request):
    author = request.user.author
    follow_objects = author.following.filter(pending='no')
    posts = Post.objects.filter(visibility='public') # all public
    posts = posts | Post.objects.filter(author=author) # all mine
    
    if follow_objects: 
        for follow in follow_objects:
            if follow.pending == 'no':

                if check_friend(follow.followed, author):
                    posts = posts | Post.objects.filter(author=follow.followed, visibility__in=['unlisted', 'friends'])
                else:
                    posts = posts | Post.objects.filter(author=follow.followed, visibility='unlisted')
    
     
    posts = posts.filter(is_deleted=False, visibility__in=['unlisted', 'friends', 'public'], content_type__in=['text/markdown', 'text/plain']).order_by("-updated_at")
    serializer = PostSerializer(posts, many=True, context={'request': request})
    posts = serializer.data
    
    structured_posts = [
        {
            "title": post.get("title", "No title"),
            "content": post.get("content", "No content"),
            "author": post.get("author", {}).get("displayName", "Unknown author"),
            "timestamp": post.get("published", "No timestamp"),
        }
        for post in posts
    ]

    formatted_data = "\n".join(
        f"Title: {post['title']}\n"
        f"Author: {post['author']}\n"
        f"Published: {post['timestamp']}\n"
        f"Content: {post['content']}\n"
        for post in structured_posts
    )
    return formatted_data