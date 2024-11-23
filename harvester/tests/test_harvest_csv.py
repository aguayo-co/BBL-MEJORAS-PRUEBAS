"""Define tests for CSV Harvesting."""
import csv
import hashlib
import os
import uuid

from django.test import TransactionTestCase

from ..functions.csv import harvest_csv_lines
from ..functions.harvester import (
    generate_file_name,
    get_storage_path,
    upload_to_storage,
)
from ..models import ContentResource, DataSource, DynamicIdentifierConfig, Set


class CsvHarvestTestCase(TransactionTestCase):
    """Test that a CSV Harvest task is properly executed."""

    initial_csv_data = [
        ["title", "creator", "description", "language", "identifier", "subject"],
        [
            "Cien Años de Soledad",
            "Gabriel García Márquez",
            "descripción uno",
            "Español",
            "identifier1",
            "Literatura",
        ],
        [
            "La Torre Oscura",
            "Stephen King",
            "descripción 2",
            "Español",
            "identifier2",
            "Literatura",
        ],
    ]
    updated_csv_data = [
        ["title", "creator", "description", "language", "identifier", "subject"],
        [
            "Cien Años de Soledad",
            "García Márquez, Gabriel",
            "descripción dos",
            "Español",
            "identifier1",
            "Novela",
        ],
        [
            "El Puño de Dios",
            "Frederick Forsyth",
            "descripción 3",
            "Español",
            "identifier3",
            "Suspenso",
        ],
    ]

    @staticmethod
    def create_data_source():
        """Create a sample data source."""
        data_source = DataSource(
            name="Sample DS",
            config={
                "url": "",
                "format": "csv",
                "method": "upload",
                "delimiter": ",",
                "quotechar": '"',
            },
            data_mapping={
                "title": ["title"],
                "creator": ["creator"],
                "subject": ["subject"],
                "language": ["language"],
                "identifier": ["identifier"],
                "description": ["description"],
                "positions": {
                    "title": 0,
                    "creator": 0,
                    "subject": 0,
                    "language": 0,
                    "identifier": 0,
                    "description": 0,
                },
            },
        )
        data_source.save()
        return data_source

    def create_csv(self, initial=True):
        """Create a Sample CSV File."""
        csv_data = self.initial_csv_data if initial else self.updated_csv_data
        csv_name = "sample_load.csv" if initial else "sample_load_updated.csv"

        path = os.path.join("media", csv_name)
        storage_path = os.path.join(
            get_storage_path(1, str(uuid.uuid1())), generate_file_name(".csv")
        )

        csv.register_dialect("quoted", quoting=csv.QUOTE_ALL, skipinitialspace=True)
        with open(path, mode="w") as csv_file:
            writer = csv.writer(csv_file, dialect="quoted")
            writer.writerows(csv_data)
        csv_file.close()

        upload_to_storage(storage_path, path)
        return storage_path

    def test_harvest_csv(self):
        """Harvest two resources for a CSV data source."""
        data_source = self.create_data_source()
        harvest_csv_lines(
            0,
            data_source,
            data_source.data_mapping,
            ("set_csv_ds_1", "Sample Set"),
            self.create_csv(True),
            "sample_group_id",
        )
        self.assertEqual(2, data_source.contentresource_set.count())

    def test_harvest_csv_updated(self):
        """Run a Updated Harvest task to delete, update and add one resource."""
        data_source = self.create_data_source()
        # First Harvest
        harvest_csv_lines(
            0,
            data_source,
            data_source.data_mapping,
            ("set_csv_ds_1", "Sample Set"),
            self.create_csv(True),
            "sample_group_id",
        )

        # Initial Validation
        self.assertEqual(
            "Gabriel García Márquez",
            ContentResource.objects.get(identifier__0="identifier1").creator[0],
        )
        # Check that resource 2 exists
        self.assertEqual(
            True, ContentResource.objects.filter(identifier__0="identifier2").exists()
        )
        # And that has one Set.
        self.assertEqual(
            True,
            ContentResource.objects.get(
                identifier__0="identifier2"
            ).setandresource_set.exists(),
        )

        # Updated Harvest
        harvest_csv_lines(
            0,
            data_source,
            data_source.data_mapping,
            ("set_csv_ds_1", "Sample Set"),
            self.create_csv(False),
            "sample_group_id_two",
        )

        # Resource removed from Set.
        self.assertEqual(
            False,
            ContentResource.objects.get(
                identifier__0="identifier2"
            ).setandresource_set.exists(),
        )
        # Resource Updated
        self.assertEqual(
            "García Márquez, Gabriel",
            ContentResource.objects.get(identifier__0="identifier1").creator[0],
        )
        # Resource Added
        self.assertEqual(
            True, ContentResource.objects.filter(identifier__0="identifier3").exists()
        )

    def test_harvest_csv_with_modified_set_name(self):
        """Verify that a set with modified name is not recreated in a second harvest."""
        data_source = self.create_data_source()

        # Initial Harvest
        harvest_csv_lines(
            0,
            data_source,
            data_source.data_mapping,
            ("set_csv_ds_1", "Sample Set"),
            self.create_csv(True),
            "sample_group_id",
        )

        # Modify Set
        set_instance = Set.objects.get(spec="set_csv_ds_1")
        set_instance.name = "Sample Set Modified"
        set_instance.save()

        # Update Harvest
        harvest_csv_lines(
            0,
            data_source,
            data_source.data_mapping,
            ("set_csv_ds_1", "Sample Set"),
            self.create_csv(True),
            "sample_group_id",
        )
        # Only one set
        self.assertEqual(1, data_source.set_set.count())

        # Is the same set
        self.assertEqual(set_instance.id, data_source.set_set.first().id)

    def test_hashed_identifier_calculation(self):
        """Test that the hashed_identifier calculation if no DynamicIdentifierConfig exists."""  # pylint: disable=line-too-long
        data_source = self.create_data_source()

        # Initial Harvest
        harvest_csv_lines(
            0,
            data_source,
            data_source.data_mapping,
            ("set_csv_ds_1", "Sample Set"),
            self.create_csv(True),
            "sample_group_id",
        )

        # Resource Updated
        self.assertEqual(
            hashlib.sha1(repr(["identifier1"]).encode("utf-8")).hexdigest(),
            ContentResource.objects.get(identifier__0="identifier1").dynamic_identifier,
        )

    def test_dynamic_identifier_is_calculated(self):
        """Test that the dynamic_identifier is calculated if DynamicIdentifierConfig exists."""  # pylint: disable=line-too-long
        data_source = self.create_data_source()
        DynamicIdentifierConfig.objects.create(
            field="identifier", capture_expression="([0-9]+)", data_source=data_source
        )

        # Initial Harvest
        harvest_csv_lines(
            0,
            data_source,
            data_source.data_mapping,
            ("set_csv_ds_1", "Sample Set"),
            self.create_csv(True),
            "sample_group_id",
        )

        # Resource Updated
        self.assertEqual(
            "1",
            ContentResource.objects.get(identifier__0="identifier1").dynamic_identifier,
        )
