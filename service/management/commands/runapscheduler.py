# runapscheduler.py
import logging
import requests
from django.utils import timezone
from author.models import Author
from post.models import Post
from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)


def fetch_github_activity_task():
    try:
        logger.info("Starting GitHub activity fetch")
        authors = Author.objects.all()
        
        for author in authors:
            if not author.github_url or author.serial == 0:
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


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way. 
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
  """
  This job deletes APScheduler job execution entries older than `max_age` from the database.
  It helps to prevent the database from filling up with old historical records that are no
  longer useful.
  
  :param max_age: The maximum length of time to retain historical job execution records.
                  Defaults to 7 days.
  """
  DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
  help = "Runs APScheduler."

  def handle(self, *args, **options):
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
      fetch_github_activity_task,
      trigger=CronTrigger(minute="*/1"),  # Every 10 seconds
      id="fetch_github_activity_task",  # The `id` assigned to each job MUST be unique
      max_instances=1,
      replace_existing=True,
    )
    logger.info("Added job 'fetch_github_activity_task'.")

    scheduler.add_job(
      delete_old_job_executions,
      trigger=CronTrigger(
        day_of_week="mon", hour="00", minute="00"
      ),  # Midnight on Monday, before start of the next work week.
      id="delete_old_job_executions",
      max_instances=1,
      replace_existing=True,
    )
    logger.info(
      "Added weekly job: 'delete_old_job_executions'."
    )

    try:
      logger.info("Starting scheduler...")
      scheduler.start()
    except KeyboardInterrupt:
      logger.info("Stopping scheduler...")
      scheduler.shutdown()
      logger.info("Scheduler shut down successfully!")
