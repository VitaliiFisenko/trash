from celery import Task
from celery.contrib import rdb
from celery.result import AsyncResult
from celery.schedules import crontab
from celery.task import periodic_task
from django.views.generic.base import View

from apps.musorka.models import Musorka
from apps.user_profile.models import UserProfile
from trash.celery import app


@app.task(name='say_hello', ignore_result=True)
def say_hello():
    print('Hello')


say_hello.apply_async()
@app.task(name='change_user_name', ignore_result=True)
def change_user_name(user_id):
    user = UserProfile.objects.get(id=user_id)
    user.username = 'Ivan'
    user.save()


schedule = {
    'task': 'change_user_name',
    'schedule': crontab(minute=5)
}

app.conf.beat_schedule.update(schedule)


class MyTask(Task):

    def run(self, *args, **kwargs):
        ...

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        pass

    def retry(self, args=None, kwargs=None, exc=None, throw=True,
              eta=None, countdown=None, max_retries=None, **options):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        pass


@app.task(name='second_task', base=MyTask)
def second_task(self):
    Musorka.objects.last().delate()
    pass


MyTask.delay()
rdb
