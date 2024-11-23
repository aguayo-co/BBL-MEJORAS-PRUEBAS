"""Define models for MegaRed app."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from resources.models import TimestampModel


class Country(TimestampModel):

    name = models.CharField(max_length=40, verbose_name=_("nombre"))
    dian_code = models.IntegerField(verbose_name=_("código Dian"))

    def __str__(self):
        return self.name

    class Meta(TimestampModel.Meta):
        """Define options for country."""

        verbose_name = _("País")
        verbose_name_plural = _("Países")

        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="mega_red_unique_country_name"
            ),
            models.UniqueConstraint(
                fields=["dian_code"], name="mega_red_unique_country_dian_code"
            ),
        ]
