from django.shortcuts import render


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import openai
openai.api_key = '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'


@csrf_exempt
def chatgpt_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the assistant's reply
            reply = response.choices[0].message['content']

            return JsonResponse({'response': reply})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

