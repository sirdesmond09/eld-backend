import factory
import factory.fuzzy
from core.choices import Gender
from core.models.accounts.user import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    class Params:
        superuser = factory.Trait(
            is_superuser=True,
            is_staff=True,
        )
        verified = factory.Trait(
            is_email_verified=True,
        )
        staff_user = factory.Trait(
            is_staff=True,
        )
        is_build = False

    email = factory.Faker("email")
    password = "A.validpassword20@"
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    gender = factory.Faker("random_element", elements=Gender.choices)
    address = factory.Faker("address")
    state = factory.Faker("state")
    country = factory.Faker("country")
