from django.contrib import admin, messages

from secretariat.models import Membership, Organisation, User
from secretariat.utils.outline import GroupCreationFailed


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    verbose_name_plural = "Organisations"


class MembershipInlineForOrganisation(MembershipInline):
    verbose_name_plural = "Membres"


class SynchronizedWithOutlineFilter(admin.SimpleListFilter):
    title = "Synchronisé avec Outline"
    parameter_name = "outline_sync"
    field_name = "outline_uuid"

    def lookups(self, request, model_admin):
        return (
            ("oui", "Oui"),
            ("non", "Non"),
        )

    def queryset(self, request, queryset):
        if self.value() == "oui":
            return queryset.filter(**{f"{self.field_name}__isnull": False})
        if self.value() == "non":
            return queryset.filter(**{f"{self.field_name}__isnull": True})


@admin.action(description="Synchroniser vers Outline")
def sync_objects_with_outline(model_admin: admin.ModelAdmin, request, queryset):
    for object in queryset:
        try:
            object.synchronize_to_outline()
            messages.success(
                request,
                f"Synchronisation correcte de l’{model_admin.opts.verbose_name} « {object}»",
            )
        except GroupCreationFailed:
            messages.error(
                request,
                f"Impossible de créer le groupe Outline « {object.name}».",
            )
        except Exception:
            messages.error(
                request,
                f"Une erreur s’est produite lors de la synchronisation de l’{model_admin.opts.verbose_name} « {object}»",
            )


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
    list_filter = (SynchronizedWithOutlineFilter,)
    inlines = [MembershipInline]
    actions = (sync_objects_with_outline,)
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


class OrganisationSynchronizedWithOutlineFilter(SynchronizedWithOutlineFilter):
    title = "Synchronisée avec Outline"
    field_name = "outline_group_uuid"


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    inlines = [MembershipInlineForOrganisation]
    actions = (sync_objects_with_outline,)
    list_filter = (OrganisationSynchronizedWithOutlineFilter,)
    list_display = (
        "name",
        "is_outline_synchronized",
    )

    @admin.display(description="Synchro Outline", boolean=True)
    def is_outline_synchronized(self, obj):
        return obj.outline_group_uuid is not None
