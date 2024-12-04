from django.shortcuts import render
import requests 
from django.urls import reverse
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
                prompt += f"Please provide the following content as a JSON object, and output only the JSON without any extra text:\n{prompt}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the assistant's reply
            reply = response.choices[0].message['content']
            # reply = r'''{
            #     "title": "Tips for Getting Good Sleep",
            #     "content": "1. Stick to a consistent sleep schedule by going to bed and waking up at the same time every day.\n2. Create a relaxing bedtime routine to signal to your body that it's time to wind down.\n3. Keep your bedroom dark, quiet, and cool to create an optimal sleep environment.\n4. Limit exposure to screens (TV, phone, computer) before bed as the blue light can disrupt your sleep.\n5. Avoid caffeine and heavy meals close to bedtime.\n6. Exercise regularly, but avoid vigorous activity too close to bedtime.\n7. Manage stress through relaxation techniques such as meditation or deep breathing.\n8. Invest in a comfortable mattress, pillows, and bedding to enhance your sleep quality.",
            #     "contentType": "text/markdown"
            # }'''
            print(reply)
            # Check if the reply is JSON-like for post creation
            if key:
                try:
                    # Use a regular expression to extract the JSON object
                    json_match = re.search(r'\{.*?\}', reply, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        json_str = json_str.replace("'", '"')
                        # Escape the newline characters
                        json_str_fixed = json_str.replace('\n', '\\n')
                        try:
                            reply_data = json.loads(json_str_fixed)
                            print("Parsed JSON:", reply_data)
                        except json.JSONDecodeError as e:
                            print("Error decoding JSON:", e)
                    else:
                        print("No JSON object found in the reply")
                    reply_data = json.loads(reply)
                    title = reply_data.get('title', '')
                    content = reply_data.get('content', '')
                    content_type = reply_data.get('contentType', '')
                    if content_type != "text/markdown" or content_type != 'text/plain':
                        content_type = 'text/markdown'
                        
                    relative_url  = reverse('post_list', args=[request.user.author.serial])  
                    backend_url = request.build_absolute_uri(relative_url)
                    
                    post_response = requests.post(
                        backend_url,
                        json={
                            'title': title,
                            'content': content,
                            'description': 'This is a post made by Aqua AI',
                            'contentType': content_type,
                            'visibility': 'PUBLIC'
                        },
                        headers={'Authorization': f'Bearer {request.auth}'}  
                    )
                    if post_response.status_code == 201:
                        return JsonResponse({'response': f'Post created successfully!'})
                    else:
                        return JsonResponse({'response': 'Someone tell Rex there is a problem with my AI.'}, status=500)

                except json.JSONDecodeError:
                    return JsonResponse({'response': json.JSONDecodeError})  # Return the original response if parsing fails
            else:
                return JsonResponse({'response': reply})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

