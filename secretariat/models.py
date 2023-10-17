from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    outline_uuid = models.CharField(max_length=36, blank=False, null=True, default=None)
