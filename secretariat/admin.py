from django.contrib import admin, messages

from secretariat.models import Membership, Organisation, User
from secretariat.utils.outline import GroupCreationFailed


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
            try:
                obj.synchronize_to_outline()
                success_message = f"L'adresse email « {obj.email} » a été invitée sur Outline et ajoutée au(x) groupe(s) adéquat(s)."
                messages.success(request, success_message)
            except Exception:
                error_message = f"L’invitation à Outline a échoué. Vérifiez que l'adresse email « {obj.email} » n'est pas déjà invitée sur Outline."
                messages.warning(request, error_message)


@admin.action(description="Synchroniser les organisations vers Outline")
def sync_organisations_with_outline(_, request, queryset):
    for organisation in queryset:
        try:
            organisation.synchronize_to_outline()
            messages.success(
                request,
                f"Le groupe « {organisation.name}» a bien été synchronisé vers Outline.",
            )
        except GroupCreationFailed:
            messages.error(
                request,
                f"Impossible de créer le groupe Outline « {organisation.name}».",
            )


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    inlines = [MembershipInlineForOrganisation]
    actions = (sync_organisations_with_outline,)
    list_display = (
        "name",
        "is_outline_synchronized",
    )

    @admin.display(description="Synchro Outline", boolean=True)
    def is_outline_synchronized(self, obj):
        return obj.outline_group_uuid is not None
