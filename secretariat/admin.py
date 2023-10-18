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
        "is_outline_synchronized",
    )
    readonly_fields = ["outline_uuid"]

    @admin.display(description="Synchro Outline", boolean=True)
    def is_outline_synchronized(self, obj):
        return obj.outline_uuid is not None

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.outline_uuid is None and "email" in form.changed_data:
            from secretariat.utils.outline import Client as OutlineClient
            from secretariat.utils.outline import InvitationFailed

            client = OutlineClient()

            try:
                obj.outline_uuid = client.invite_to_outline(obj)
                obj.save()
                client.add_to_outline_group(
                    user_uuid=obj.outline_uuid, group=OUTLINE_OPI_GROUP_ID
                )
                success_message = f"L'adresse email « {obj.email} » invitée sur Outline et ajoutée au groupe Opérateur."
                messages.success(request, success_message)
            except InvitationFailed:
                error_message = f"L’invitation à Outline a échoué. Vérifiez que l'adresse email « {obj.email} » n'est pas déjà invitée sur Outline."
                messages.warning(request, error_message)
