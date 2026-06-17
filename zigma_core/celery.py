import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zigma_core.settings.dev')

app = Celery('zigma_core')

# Bind settings using the CELERY_ namespace prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Scan all subfolders inside the apps/ directory for a tasks.py file automatically
app.autodiscover_tasks()