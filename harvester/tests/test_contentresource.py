"""Define tests for :model:`harvester.ContentResource`."""
import datetime
from datetime import date, timedelta

from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from ..models import (
    Collection,
    CollectionAndResource,
    ContentResource,
    DataSource,
    Equivalence,
)
from .utils import TestUtilitiesMixin


class YearTestCase(TestCase):
    """Test that year is properly extracted from date."""

    def test_date_is_not_found(self):
        """Year information is not found in the date field."""
        dates = ["0000", "000-", "00--", "00-?", "12345", "z1234", "1234z", "z1234z"]
        for value in dates:
            with self.subTest(value):
                resource = ContentResource(date=[value])
                self.assertEqual(None, resource.processed_data.date)

    def test_date_is_complete(self):
        """Year a full date is found."""
        dates = [
            # ISO or similar formats
            (date(1990, 2, 3), " 1990/02/3 "),
            (date(1990, 2, 3), "/1990/02/3/"),
            (date(1990, 2, 3), "1990/02/3"),
            (date(1990, 2, 3), "1990-02-3"),
            (date(1990, 2, 3), "1990/2/03"),
            (date(1990, 2, 3), "1990-2-03"),
            (date(1990, 2, 3), "1990/02/03"),
            (date(1990, 2, 3), "1990-02-03"),
            (date(1990, 12, 31), "1990/12/31"),
            # US format
            (date(1991, 2, 3), "3/2/1991"),
            (date(1991, 12, 31), "31/12/1991"),
        ]
        for year, value in dates:
            with self.subTest(value):
                resource = ContentResource(date=[value])
                self.assertEqual(year, resource.processed_data.date)

    def test_date_from_year(self):
        """Year information is present and is found as a year."""
        dates = [
            (date(1990, 1, 1), "c1990"),
            (date(1990, 1, 1), "c.1990"),
            (date(1990, 1, 1), "1990"),
            (date(1991, 1, 1), "1991 "),
            (date(1991, 1, 1), " 1991"),
            (date(1991, 1, 1), " 1991 "),
            (date(1991, 1, 1), " 1991-"),
            (date(1991, 1, 1), "-1991 "),
            (date(1991, 1, 1), "-1991-"),
            (date(1991, 1, 1), "/1991"),
            (date(1991, 1, 1), "1991/"),
            (date(1991, 1, 1), "1991/"),
            (date(1991, 1, 1), "0000-1991"),
            (date(1992, 1, 1), "1992/13/01"),
            (date(1992, 1, 1), "1992/12/33"),
            (date(1993, 1, 1), "33/12/1993"),
            (date(1993, 1, 1), "30/13/1993"),
        ]
        for year, value in dates:
            with self.subTest(value):
                resource = ContentResource(date=[value])
                self.assertEqual(year, resource.processed_data.date)

    def test_date_from_decade(self):
        """Year information is present and is found  as a decade."""
        dates = [(date(2010, 1, 1), "201-"), (date(2010, 1, 1), "201?")]
        for year, value in dates:
            with self.subTest(value):
                resource = ContentResource(date=[value])
                self.assertEqual(year, resource.processed_data.date)

    def test_date_from_century(self):
        """Year information is present and is found as a century."""
        dates = [
            (date(2100, 1, 1), "21--"),
            (date(2100, 1, 1), "21-?"),
            (date(2100, 1, 1), "21-?-"),
            (date(2100, 1, 1), "21-?-220-"),
            (date(2100, 1, 1), "21-?-220?"),
            (date(2100, 1, 1), "21-?-2200"),
        ]
        for year, value in dates:
            with self.subTest(value):
                resource = ContentResource(date=[value])
                self.assertEqual(year, resource.processed_data.date)

    def test_year_is_formatted(self):
        """Year information is properly formatted."""
        dates = [
            ("1990", "1990/1/1"),
            ("1990", "1990"),
            ("Ca. 1990", "1990-1991"),
            ("Ca. 1990", "c1990"),
            ("Ca. 1990", "199-"),
            ("Ca. 1990", "1990/13/32"),
            ("Century ⅩⅨ", "19--"),
            ("Century ⅩⅩ", "20--"),
        ]
        data_source = DataSource.objects.create(name="Sample DS")
        resource = ContentResource.objects.create(
            data_source=data_source, identifier=["identifier"]
        )
        for year, value in dates:
            with self.subTest(value):
                resource.date = [value]
                self.assertEqual(year, resource.processed_data.formatted_date)

    def test_date_is_formatted(self):
        """Date information is properly formatted."""
        equivalence = Equivalence.objects.create(
            name="Full date format", field="type", cite_type="standard", full_date=True
        )
        data_source = DataSource.objects.create(name="Sample DS")
        resource = ContentResource.objects.create(
            date=["1990/03/02"], data_source=data_source, identifier=["identifier"]
        )
        cr_equivalence = resource.type.create(
            original_value="full_date_type",
            field="type",
            equivalence=equivalence,
            through_defaults={"position": 0},
        )
        cr_equivalence.save()
        self.assertEqual("02/03/1990", resource.processed_data.formatted_date)


class CreatorTestCase(TestCase):
    """Test that creator is properly formatted."""

    def test_last_name_was_first(self):
        """Last name came before the first name."""
        resource = ContentResource(creator=["López Perez, Mateo"])
        self.assertEqual("Mateo López Perez", resource.processed_data.creator)

    def test_last_name_was_first_with_extra_data(self):
        """Last name came before the first name, and there was extra info."""
        resource = ContentResource(creator=["López Perez, Mateo, 1985"])
        self.assertEqual("Mateo López Perez", resource.processed_data.creator)

    def test_name_was_already_formatted(self):
        """Name was already formatted, or was not formattable."""
        resource = ContentResource(creator=["Mateo López Perez"])
        self.assertEqual("Mateo López Perez", resource.processed_data.creator)

    def test_name_is_stripped(self):
        """Name was already formatted, or was not formattable."""
        resource = ContentResource(creator=[" Mateo López Perez "])
        self.assertEqual("Mateo López Perez", resource.processed_data.creator)


class DefaultProcessorTestCase(TestCase):
    """Test behavior of default processor."""

    def test_non_existing_property(self):
        """Test AttributeError is raised for non existing property."""
        resource = ContentResource()
        with self.assertRaises(AttributeError):
            resource.processed_data.test_property  # pylint: disable=pointless-statement

    def test_first_element_of_property(self):
        """Test AttributeError is raised for non existing property."""
        resource = ContentResource()
        values = ["first element", "second element"]
        resource.test_property = values
        self.assertEqual(resource.processed_data.test_property, values[0])

    def test_none_for_empty_properties(self):
        """Test AttributeError is raised for non existing property."""
        resource = ContentResource()
        resource.test_property = []
        self.assertEqual(resource.processed_data.test_property, None)


class CalculatedFieldsTestCase(TestCase):
    """Test behavior of calculated fields mixin."""

    calculated_fields_values = {
        "calculated_group_hash": f"hash_{timezone.now()}",
        "calculated_date": timezone.now(),
    }

    def test_date_is_calculated(self):
        """Test AttributeError is raised for non existing property."""

        data_source = DataSource.objects.create(name="sample")
        with self.subTest("sample_date"):
            resource = ContentResource.objects.create(
                date=["1990/12/31"],
                identifier=["identifier_1"],
                data_source=data_source,
            )
            self.assertEqual(None, resource.calculated_date)
            resource.calculate_fields()
            self.assertEqual(date(1990, 12, 31), resource.calculated_date)

    def test_need_recalculation(self):
        """Test if resources need to be recalculated."""

        data_source = DataSource.objects.create(name="sample")
        with self.subTest("force recalculation"):
            resource = ContentResource.objects.create(
                identifier=["identifier_1"],
                data_source=data_source,
                force_calculation=True,
                **self.calculated_fields_values,
            )
            self.assertTrue(
                ContentResource.outdated_objects.filter(pk=resource.id).exists()
            )

        with self.subTest("updated_at > calculation_at"):
            resource = ContentResource.objects.create(
                identifier=["identifier_2"],
                data_source=data_source,
                calculation_at=timezone.now(),
                **self.calculated_fields_values,
            )
            self.assertTrue(
                ContentResource.outdated_objects.filter(pk=resource.id).exists()
            )

    def test_does_not_need_recalculation(self):
        """Test that a resources does not need to be recalculated."""

        # Null values should not trigger recalculation.
        missing_calculated_field = self.calculated_fields_values.copy()
        missing_calculated_field.pop("calculated_date")

        data_source = DataSource.objects.create(name="sample")
        ContentResource.objects.create(
            identifier=["identifier_1"],
            data_source=data_source,
            calculation_at=timezone.now() + timedelta(seconds=2),
            **missing_calculated_field,
        )
        self.assertEqual(0, ContentResource.outdated_objects.count())


class ContentResourceCachedFieldsTestCase(TestUtilitiesMixin, TransactionTestCase):
    """Test behavior of cached fields mixin."""

    def test_cached_collection_count_field(self):
        """Check that the collection_count cached field is calculated."""
        collections_to_create = 10
        user = self.get_user()
        data_source = self.get_data_source()

        resource = ContentResource.objects.create(
            identifier=["identifier_one"],
            data_source=data_source,
            calculation_at=timezone.now(),
        )

        with self.subTest("Count is 0 by default"):
            self.assertEqual(resource.collection_count, None)

        # Add Collections
        for i in range(0, collections_to_create):
            collection = Collection.objects.create(
                title=f"Sample Collection {i}",
                description="This is a Sample Collection",
                image=self.get_image(),
                owner=user,
                public=True,
            )
            CollectionAndResource.objects.create(
                collection=collection, resource=resource
            )

        resource.collection_count_expiration = timezone.now() - datetime.timedelta(
            hours=1
        )

        with self.subTest("Returns cached value"):
            self.assertEqual(resource.collection_count, None)

        resource.update_expired_fields()
        with self.subTest("Check Collection Calculation"):
            self.assertEqual(resource.collection_count, collections_to_create)
