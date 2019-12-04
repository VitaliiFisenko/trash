from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
from apps.core.files_paths import user_photo_path
from trash.storage import OverwriteStorage


class UserProfile(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?[ (\-\d)]+$',
                                 message='Номер телефону повинен бути введений в форматі: "+999999999". '
                                         'До 12 цифр допускається.')
    photo = models.ImageField(verbose_name='Фото', upload_to=user_photo_path, blank=True,
                              storage=OverwriteStorage())
    phone_number = models.CharField(verbose_name='Номер телефону', validators=[phone_regex], max_length=50, blank=True,
                                    null=True)


