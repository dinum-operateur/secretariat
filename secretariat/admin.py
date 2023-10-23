from django.contrib import admin, messages

from config.settings import OUTLINE_OPI_GROUP_ID
from secretariat.models import Membership, Organisation, User


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    verbose_name_plural = "Organisations"


class MembershipInlineForOrganisation(MembershipInline):
    verbose_name_plural = "Membres"


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
    inlines = [MembershipInline]
    readonly_fields = ["outline_uuid"]
    fieldsets = (
        (
            "Utilisateur/rice",
            {
                "fields": ("username", "password", "email", "first_name", "last_name"),
            },
        ),
        (
            "Synchronisation",
            {
                "fields": ("outline_uuid", "date_joined"),
            },
        ),
        (
            "Django",
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
    )

    @admin.display(description="Synchro Outline", boolean=True)
    def is_outline_synchronized(self, obj):
        return obj.outline_uuid is not None

    def save_model(self, request, obj: User, form, change):
        super().save_model(request, obj, form, change)

        if "password" in form.changed_data:
            obj.set_password(form.data["password"])
            obj.save()

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


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    inlines = [MembershipInlineForOrganisation]
