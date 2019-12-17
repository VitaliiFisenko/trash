from colorful.fields import RGBColorField
from django.db import models

# Create your models here.
from django_extensions.db.models import TimeStampedModel

from apps.core.files_paths import musorka_image_path
from apps.user_profile.models import UserProfile


class Musorka(TimeStampedModel):

    EMPTY = 1
    FULL = 2



    STATUS_CHOICES = ((EMPTY, 'empty'), (FULL, 'full'))

    status = models.IntegerField(choices=STATUS_CHOICES, default=EMPTY)

    volume = models.PositiveIntegerField()

    counter = models.PositiveIntegerField(default=0)

    color = RGBColorField()

    image = models.ImageField(max_length=255, upload_to=musorka_image_path, blank=True)

    matherial = models.CharField(max_length=100, blank=True)

    description = models.TextField(max_length=500, blank=True)

    user = models.ManyToManyField(UserProfile, related_name='musorka', related_query_name='musorka')


class MusorkaHistoryModel(models.Model):

    EMPTY = 1
    FULL = 2

    STATUS_CHOICES = (
        (EMPTY, 'empty'),
        (FULL, 'full')
    )

    musorka = models.ForeignKey(Musorka, related_name='history', on_delete=models.PROTECT)

    empty_time = models.DateTimeField(null=True)

    full_time = models.DateTimeField(null=True)

    status = models.IntegerField(choices=STATUS_CHOICES, default=EMPTY)

    counter = models.PositiveIntegerField(default=0)

# знаем количество опусташений мусорки + время последнего заполнения
