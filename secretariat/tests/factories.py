import factory
from factory import Faker, LazyAttribute
from factory.django import DjangoModelFactory
from unidecode import unidecode

import secretariat.models as models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = models.User

    first_name = Faker("first_name", locale="fr_FR")
    last_name = Faker("last_name", locale="fr_FR")
    username = LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}")
    email = LazyAttribute(lambda o: f"{unidecode(o.username)}@fictif.pour.test.gouv.fr")
    password = Faker("password")


class UserSynchronizedWithOutlineFactory(UserFactory):
    outline_uuid = Faker("uuid4")


class OrganisationFactory(DjangoModelFactory):
    class Meta:
        model = models.Organisation

    name = Faker("company", locale="fr_FR")


class OrganisationSynchronizedWithOutlineFactory(OrganisationFactory):
    outline_group_uuid = Faker("uuid4")


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = models.Membership

    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)
    role = "member"
