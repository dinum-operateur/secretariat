from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    outline_uuid = models.UUIDField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def organisations(self):
        return Organisation.objects.filter(membership__user=self)

    def synchronize_outline(self):
        from secretariat.utils.outline import Client as OutlineClient
        from secretariat.utils.outline import InvitationFailed

        client = OutlineClient()

        if not self.outline_uuid:
            try:
                self.outline_uuid = client.invite_to_outline(self)
                self.save()
            except InvitationFailed:
                outline_user = client.find_user_from_email(self.email)
                self.outline_uuid = outline_user["id"]
                self.save()

        for group in self.organisations:
            if group.outline_uuid:
                client.add_to_outline_group(self.outline_uuid, group.outline_group_uuid)


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
