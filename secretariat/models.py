from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, F, Q


class User(AbstractUser):
    outline_uuid = models.UUIDField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def organisations(self):
        return Organisation.objects.filter(membership__user=self)

    def synchronize_to_outline(self):
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
            if group.outline_group_uuid:
                client.add_to_outline_group(self.outline_uuid, group.outline_group_uuid)


class Organisation(models.Model):
    name = models.CharField(max_length=50)
    outline_group_uuid = models.UUIDField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name

    @property
    def members(self):
        return User.objects.filter(membership__organisation=self)

    def synchronize_to_outline(self):
        from secretariat.utils.outline import Client as OutlineClient
        from secretariat.utils.outline import GroupCreationFailed

        client = OutlineClient()

        if not self.outline_group_uuid:
            try:
                self.outline_group_uuid = client.create_new_group(self.name)
                self.save()
            except GroupCreationFailed:
                outline_user = client.find_group_by_name(self.name)
                self.outline_group_uuid = outline_user["id"]
                self.save()

        # create users on outline when needed
        for new_member in self.members.filter(outline_uuid__isnull=True):
            new_member.synchronize_to_outline()

        # find users which already are in the group on outline side:
        # no need to add them again
        user_uuids_in_outline_group = set(
            user.get("id") for user in client.list_group_users(self.outline_group_uuid)
        )

        # add outline users to outline group when possible and needed
        for new_member in self.members.filter(outline_uuid__isnull=False).exclude(
            outline_uuid__in=user_uuids_in_outline_group
        ):
            client.add_to_outline_group(
                new_member.outline_uuid, self.outline_group_uuid
            )

        # remove users from outline group which are not in django group
        user_uuids_in_django_group = set(
            str(value[0]) for value in self.members.values_list("outline_uuid")
        )
        user_uuids_to_remove_from_outline_group = (
            user_uuids_in_outline_group - user_uuids_in_django_group
        )
        for uuid in user_uuids_to_remove_from_outline_group:
            client.remove_from_outline_group(uuid, self.outline_group_uuid)


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    role = models.CharField(max_length=15)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(end_date__gt=F("start_date")),
                name="start_must_be_before_end",
            ),
        ]

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "La date de fin ne peut pas être avant la date de début."}
            )
