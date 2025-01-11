import os

from celery import Celery
from decouple import config
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gimsap.settings')

app = Celery('Gimsap')
# used redis broker if it exists
if config('BROKER') == 'REDIS':
    app = Celery('Gimsap', broker_url=config('REDISTOGO_URL'))

app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    """
    Example should look like this
    'send_admin_message': {
        'task': 'home.tasks.send_admin',
        'schedule': 86400,
    },"""
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
