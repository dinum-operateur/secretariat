from django.test import TestCase, tag

from secretariat.admin import (
    OrganisationAdmin,
    OrganisationSynchronizedWithOutlineFilter,
    SynchronizedWithOutlineFilter,
    UserAdmin,
)
from secretariat.models import Organisation, User
from secretariat.tests.factories import (
    OrganisationFactory,
    OrganisationSynchronizedWithOutlineFactory,
    UserFactory,
    UserSynchronizedWithOutlineFactory,
)


@tag("admin")
class OutlineSyncFilterTests(TestCase):
    def test_queryset_organisations(self):
        OrganisationFactory()
        OrganisationFactory()
        synced_org = OrganisationSynchronizedWithOutlineFactory()
        synchronized_filter = OrganisationSynchronizedWithOutlineFilter(
            None,
            {"outline_sync": "oui"},
            Organisation,
            OrganisationAdmin,
        )
        queryset_synchronized = synchronized_filter.queryset(
            None, Organisation.objects.all()
        )
        self.assertEqual(1, queryset_synchronized.count())
        self.assertEqual(
            str(synced_org.outline_group_uuid),
            str(queryset_synchronized[0].outline_group_uuid),
        )

        unsynchronized_filter = OrganisationSynchronizedWithOutlineFilter(
            None,
            {"outline_sync": "non"},
            Organisation,
            OrganisationAdmin,
        )
        queryset_unsynchronized = unsynchronized_filter.queryset(
            None, Organisation.objects.all()
        )
        self.assertEqual(2, queryset_unsynchronized.count())
        self.assertIsNone(queryset_unsynchronized[0].outline_group_uuid)

    def test_queryset_users(self):
        UserFactory()
        UserFactory()
        synced_user = UserSynchronizedWithOutlineFactory()
        synchronized_filter = SynchronizedWithOutlineFilter(
            None,
            {"outline_sync": "oui"},
            User,
            UserAdmin,
        )
        queryset_synchronized = synchronized_filter.queryset(None, User.objects.all())
        self.assertEqual(1, queryset_synchronized.count())
        self.assertEqual(
            str(synced_user.outline_uuid),
            str(queryset_synchronized[0].outline_uuid),
        )

        unsynchronized_filter = SynchronizedWithOutlineFilter(
            None,
            {"outline_sync": "non"},
            Organisation,
            OrganisationAdmin,
        )
        queryset_unsynchronized = unsynchronized_filter.queryset(
            None, User.objects.all()
        )
        self.assertEqual(2, queryset_unsynchronized.count())
        self.assertIsNone(queryset_unsynchronized[0].outline_uuid)
