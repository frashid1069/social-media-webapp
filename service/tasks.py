# service/tasks.py
from background_task import background
import requests
from django.utils import timezone
from .models import Author
from post.models import Post
import logging

logger = logging.getLogger(__name__)

@background(schedule=60)
def fetch_github_activity_task():
    try:
        logger.info("Starting GitHub activity fetch")
        authors = Author.objects.all()
        
        for author in authors:
            if not author.github_url:
                continue
                
            github_username = author.github_url.rstrip('/').split('/')[-1]
            url = f'https://api.github.com/users/{github_username}/events/public'
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                events = response.json()
                created_count = 0
                
                for event in events:
                    event_type = event['type']
                    event_id = event['id']
                    
                    if Post.objects.filter(github_event_id=event_id).exists():
                        continue
                    elif event_type != 'PushEvent':
                        continue
                    
                    title = f"{event_type} on {event['repo']['name']}"
                    content = f"Event data: {event['payload']}"
                    
                    Post.objects.create(
                        author=author,
                        title=title,
                        content=content,
                        created_at=timezone.now(),
                        github_event_id=event_id
                    )
                    created_count += 1
                
                logger.info(f"Created {created_count} new posts for {github_username}")
            else:
                logger.error(f"Failed to fetch GitHub events for {github_username}. Status code: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error in fetch_github_activity_task: {str(e)}")
        raise