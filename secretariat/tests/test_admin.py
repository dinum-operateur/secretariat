from django.test import TestCase, tag

from secretariat.admin import (
    OrganisationAdmin,
    OrganisationSynchronizedWithOutlineFilter,
)
from secretariat.models import Organisation
from secretariat.tests.factories import (
    OrganisationFactory,
    OrganisationSynchronizedWithOutlineFactory,
)


@tag("admin")
class OutlineSyncFilterTests(TestCase):
    def test_queryset(self):
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
