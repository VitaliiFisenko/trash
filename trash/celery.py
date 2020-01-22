import os

import celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trash.settings')
app = celery.Celery(namespace='CELERY', main='trash', config_source='django.conf:settings')
app.autodiscover_tasks()

app.conf.update({

})