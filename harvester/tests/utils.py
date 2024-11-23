from django.core.files.uploadedfile import SimpleUploadedFile

from custom_user.models import User

from ..models import DataSource


class TestUtilitiesMixin:
    """Common methods for use in tests."""

    @staticmethod
    def get_image():
        """Return an instance of SimpleUploadedFile with an image."""
        return SimpleUploadedFile(
            name="test_image.png",
            content=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00IEND\xaeB`\x82",
            content_type="image/png",
        )

    @staticmethod
    def get_user():
        """Create a valid user."""
        return User.objects.create(
            first_name="Test User", username="test", password="testUser1"
        )

    @staticmethod
    def get_data_source():
        """Create a valid data_source."""
        return DataSource.objects.create(name="sample")
