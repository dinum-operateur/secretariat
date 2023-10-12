from django.contrib.auth.models import AbstractUser
from django.db import models

from config.settings import OUTLINE_OPI_GROUP_ID


class User(AbstractUser):
    outline_uuid = models.CharField(max_length=36, blank=False, null=True, default=None)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

        if self.outline_uuid is None:
            from secretariat.utils.outline import Client as OutlineClient

            client = OutlineClient()

            self.outline_uuid = client.invite_to_outline(self)
            self.save()
            client.add_to_outline_group(
                user_uuid=self.outline_uuid, group=OUTLINE_OPI_GROUP_ID
            )
