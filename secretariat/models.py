from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    outline_uuid = models.UUIDField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def organisations(self):
        return Organisation.objects.filter(membership__user=self)


class Organisation(models.Model):
    name = models.CharField(max_length=50)
    outline_group_uuid = models.UUIDField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name

    @property
    def members(self):
        return User.objects.filter(membership__organisation=self)


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    role = models.CharField(max_length=15)
