"""Define tests for Collection Related Cases."""
import datetime
import os

from django.conf import settings
from django.core.cache import cache
from django.test import TransactionTestCase
from django.utils import timezone

from ..models import (
    CollaborativeCollection,
    Collection,
    CollectionAndResource,
    ContentResource,
    Equivalence,
)
from .utils import TestUtilitiesMixin


class CollectionDetailImageTestCase(TestUtilitiesMixin, TransactionTestCase):
    """
    Test that `detail_image` is correctly assigned to :model:`hervester.Collection`.

    Every :model:`hervester.Collection` should have a randomly assigned `detail_image`.
    """

    @staticmethod
    def get_available_images():
        """Return a set of valid images for the FilePathField."""
        non_static_path = os.path.join(settings.BASE_DIR, "resources", "static")
        return {
            os.path.relpath(image_path, non_static_path)
            for image_path in dict(
                Collection._meta.get_field("detail_image").formfield().choices
            )
        }

    def test_assign_unique_n_images_to_n_collections(self):
        """Test that for N images N collections get each a different image."""
        available_images = self.get_available_images()
        used_images = []
        uploaded_image = self.get_image()
        user = self.get_user()
        # Ensure cache is empty (cache is retained between tests)
        cache.clear()

        for index in available_images:
            collection = Collection.objects.create(
                title=f"Sample Collection {index}",
                description="This is a Sample Collection",
                image=uploaded_image,
                owner=user,
                public=True,
            )
            used_images.append(collection.detail_image)
        self.assertEqual(available_images, set(used_images))

    def test_assign_detail_image_to_collection(self):
        """Test a Collection gets a detail image."""
        collection = Collection.objects.create(
            title="Sample Collection",
            description="This is a Sample Collection",
            image=self.get_image(),
            owner=self.get_user(),
            public=True,
        )
        self.assertIn(collection.detail_image, self.get_available_images())

    def test_assign_detail_image_to_collaborative_collection(self):
        """Test a CollaborativeCollection gets a detail image."""
        collaborative_collection = CollaborativeCollection.objects.create(
            title="Sample Collection",
            description="This is a Sample Collection",
            image=self.get_image(),
            owner=self.get_user(),
            public=True,
        )
        with self.subTest("As instance of CollaborativeCollection"):
            self.assertIn(
                collaborative_collection.detail_image, self.get_available_images()
            )

        collection = collaborative_collection.collection_ptr
        collection.detail_image = None
        collection.save()
        with self.subTest("As instance of Collection"):
            self.assertIn(collection.detail_image, self.get_available_images())

    def test_assign_invalid_image_to_collection(self):
        """Test to fix an invalid image in a new collection."""
        invalid_image_path = "/invalid/image/path.png"
        collection = Collection.objects.create(
            title="Sample Collection",
            description="This is a Sample Collection",
            image=self.get_image(),
            owner=self.get_user(),
            public=True,
            detail_image=invalid_image_path,
        )
        self.assertNotEqual(invalid_image_path, collection.detail_image)
        self.assertIn(collection.detail_image, self.get_available_images())


class CollectionCalculatedFieldTestCase(TestUtilitiesMixin, TransactionTestCase):
    """Test behavior of cached fields mixin."""

    def test_cached_field_resource_count(self):
        """Check if cached field works for collections."""
        collection = Collection.objects.create(
            title="Sample Collection",
            description="This is a Sample Collection",
            image=self.get_image(),
            owner=self.get_user(),
            public=True,
        )
        resources_to_create = 10

        with self.subTest("Value doesn't exists"):
            self.assertEqual(collection.resources_count, None)

        collection.refresh_from_db()

        with self.subTest("Value is calculated"):
            self.assertEqual(collection.resources_count, None)

        # Add Resources
        data_source = self.get_data_source()
        for i in range(0, resources_to_create):
            resource = ContentResource.objects.create(
                identifier=[f"identifier_{i}"],
                data_source=data_source,
                calculation_at=timezone.now(),
            )
            CollectionAndResource.objects.create(
                resource=resource, collection=collection
            )

        collection.resources_count_expiration = timezone.now() - datetime.timedelta(
            hours=1
        )

        with self.subTest("Returns cached value"):
            self.assertEqual(collection.resources_count, None)

        collection.update_expired_fields()
        with self.subTest("Check Calculation"):
            self.assertEqual(collection.resources_count, resources_to_create)
