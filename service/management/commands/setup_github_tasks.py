from django.core.management.base import BaseCommand
import requests
from author.models import Author
from post.models import Post
from django.utils import timezone
from background_task.models import Task
from service.tasks import fetch_github_activity_task



class Command(BaseCommand):
    help = 'Sets up GitHub activity fetching background tasks'

    def handle(self, *args, **options):
        # Clear any existing scheduled tasks
        Task.objects.filter(task_name='service.tasks.fetch_github_activity_task').delete()
        
        fetch_github_activity_task(repeat=10, repeat_until=None)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully scheduled GitHub activity fetching task')
        )

    # def handle(self, *args, **kwargs):
    #     authors = Author.objects.all()
    #     for author in authors:
    #         github_username = author.github_url.rstrip('/').split('/')[-1]
    #         url = f'https://api.github.com/users/{github_username}/events/public'
    #         response = requests.get(url)

    #         if response.status_code == 200:
    #             events = response.json()
    #             for event in events:
    #                 event_type = event['type']
    #                 event_id = event['id']  # Unique GitHub event ID
    #                 title = f"{event_type} on {event['repo']['name']}"
    #                 content = f"Event data: {event['payload']}"
                    
    #                 if Post.objects.filter(github_event_id=event_id).exists():
    #                     continue
                    
    #                 Post.objects.create(
    #                     author=author,
    #                     title=title,
    #                     content=content,
    #                     created_at=timezone.now(),
    #                     github_event_id=event_id  
    #                 )
                            
                            
