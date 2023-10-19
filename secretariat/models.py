from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    outline_uuid = models.UUIDField(null=True, blank=True, default=None)


class Organisation(models.Model):
    name = models.CharField(max_length=50)
    outline_group_uuid = models.UUIDField(null=True, blank=True, default=None)


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    role = models.CharField(max_length=15)
