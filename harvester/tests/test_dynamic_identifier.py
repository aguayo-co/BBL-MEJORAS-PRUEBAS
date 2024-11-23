"""Define tests for Dynamic identifier."""

from django.test import TransactionTestCase

from ..models import ContentResource, DataSource, DynamicIdentifierConfig


class DynamicIdentifierTestCase(TransactionTestCase):
    """Test Dynamic Identifier Update Cases."""

    def test_dynamic_identifier_is_updated(self):
        """Test that a dynamic identifier is updated after expiration."""
        data_source = DataSource.objects.create(name="Sample DS")
        DynamicIdentifierConfig.objects.create(
            field="identifier", capture_expression="([0-9]+)", data_source=data_source
        )
        resource = ContentResource.objects.create(
            data_source=data_source, identifier=["identifier1"]
        )

        # Expire Dynamic Identifier
        DynamicIdentifierConfig.objects.create(
            field="identifier", capture_expression="([a-z]+)", data_source=data_source
        )
        data_source.contentresource_set.update(dynamic_identifier_expired=True)

        resource.refresh_from_db()

        with self.subTest("Dynamic Identifier Is Expired"):
            self.assertEqual(
                resource.dynamic_identifier_expired,
                True,
            )

        # Initial Dynamic Identifier
        with self.subTest("Dynamic Identifier Is Numerical"):
            self.assertEqual("1", resource.dynamic_identifier)

        resource.update_expired_fields()
        resource.save()

        with self.subTest("Dynamic Identifier Is Updated"):
            self.assertEqual(
                "identifier|1",
                resource.dynamic_identifier,
            )
