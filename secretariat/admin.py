from django.contrib import admin, messages

from config.settings import OUTLINE_OPI_GROUP_ID
from secretariat.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    readonly_fields = ["outline_uuid"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if "email" in form.changed_data:
            from secretariat.utils.outline import Client as OutlineClient
            from secretariat.utils.outline import InvitationFailed

            client = OutlineClient()

            try:
                obj.outline_uuid = client.invite_to_outline(obj)
                obj.save()
                client.add_to_outline_group(
                    user_uuid=obj.outline_uuid, group=OUTLINE_OPI_GROUP_ID
                )
            except InvitationFailed:
                error_message = f"L’invitation à Outline a échoué. Vérifiez que l'adresse email « {obj.email} » n'est pas déjà invitée sur Outline."
                messages.warning(request, error_message)
