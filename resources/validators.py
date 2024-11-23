"""Define validators doe Resources app."""
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from tomlkit import parse
from tomlkit.exceptions import TOMLKitError


@deconstructible
class HtmlMaxLengthValidator(MaxLengthValidator):
    """Validate length of HTML text without the html tags."""

    def clean(self, x):
        r"""
        Convert HTML text to plain text and return its length.

        It counts <p></p> and <br> tags as two characters "  ".
        """
        normalized_value = x.replace("\r\n", "\n").replace("\r", "\n")
        # HTML present in text.
        if normalized_value != bleach.clean(normalized_value, tags=[], strip=True):
            x = (
                x.replace("</p>", "</p>  ")
                .replace("<br", "  <br")
                .replace("\r\n", "")
                .replace("\r", "")
                .replace("\n", "")
            )
            # Last aragraph should not have a space added.
            # This inflates the count by 2, which is not right.
            if x.endswith("</p>  "):
                x = x.rstrip()
            x = bleach.clean(x, tags=[], strip=True)
        return super().clean(x)


def validate_toml(value):
    """Validate that the value is a valid TOML."""
    message = _("No es un formato TOML válido. [%(error)s]")
    code = "invalid_toml"
    try:
        parse(value)
    except TOMLKitError as error:
        raise ValidationError(message, code=code, params={"error": error})


@deconstructible
class FileSizeValidator:
    """Validate the maximum size of a  file."""

    message = _("El tamaño máximo para los archivos es %(megabytes)sMB")
    code = "invalid_size"

    def __init__(self, max_size, message=None, code=None):
        """Set validator properties."""
        self.max_size = max_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        """Validate size and throw error if not valid."""
        if value.size > self.max_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={"megabytes": self.max_size / 1000000},
            )

    def __eq__(self, other):
        """Run rich equality comparison to other object."""
        return (
            isinstance(other, self.__class__)
            and self.max_size == other.max_size
            and self.message == other.message
            and self.code == other.code
        )
