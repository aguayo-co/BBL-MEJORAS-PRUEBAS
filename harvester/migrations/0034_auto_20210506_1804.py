# Generated by Django 2.2.10 on 2021-05-06 18:04

from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import gm2m.fields
import resources.fields


class Migration(migrations.Migration):

    dependencies = [
        ("harvester", "0033_auto_20210429_1447"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="adminnotification",
            options={
                "ordering": ["-updated_at"],
                "verbose_name": "administrador de notificación",
                "verbose_name_plural": "administrador de notificaciones",
            },
        ),
        migrations.AlterModelOptions(
            name="promotedcontentresource",
            options={
                "ordering": ["priority", "-updated_at"],
                "verbose_name": "recurso de contenido promocionado",
                "verbose_name_plural": "recursos de contenido promocionado",
            },
        ),
        migrations.AlterField(
            model_name="adminnotification",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.ContentType",
                verbose_name="tipo contenido",
            ),
        ),
        migrations.AlterField(
            model_name="adminnotification",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="adminnotification",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="collaborator",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="collaborator",
            name="status",
            field=models.SmallIntegerField(
                choices=[(-1, "invitado"), (-2, "solicitado"), (1, "colaborando")],
                help_text="Un usuario puede colaborar en una colección cuando su estado es 'colaborando'",
                verbose_name="estado",
            ),
        ),
        migrations.AlterField(
            model_name="collaborator",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="collaborator",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="usuario",
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="collection",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="dueño",
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="collectionandresource",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="collectionandresource",
            name="resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collectionandresource",
                to="harvester.ContentResource",
                verbose_name="recurso",
            ),
        ),
        migrations.AlterField(
            model_name="collectionandresource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="collectionsgroup",
            name="collections",
            field=gm2m.fields.GM2MField(
                through="harvester.CollectionsGroupCollection",
                through_fields=[
                    "collections_group",
                    "content_object",
                    "content_type",
                    "object_pk",
                ],
                verbose_name="colecciones",
            ),
        ),
        migrations.AlterField(
            model_name="collectionsgroup",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="collectionsgroup",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="dueño",
            ),
        ),
        migrations.AlterField(
            model_name="collectionsgroup",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="collectionsgroupcollection",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="collectionsgroupcollection",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="abstract",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="resumen",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="accessRights",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="acceso correcto",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="accrualMethod",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="método acumulación",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="accrualPeriodicity",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="periodicidad de acumulación",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="accrualPolicy",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="política de acumulación",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="alternative",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="alternativa",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="audience",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="audiencia",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="available",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="disponible",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="bibliographicCitation",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="cita bibliográfica",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="conformsTo",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="de acuerdo a",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="contributor",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="colaborador",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="coverage",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="cobertura",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="created",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="creado",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="creator",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="creador",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="data_source",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="harvester.DataSource",
                verbose_name="fuente de datos",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="date",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="fecha",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="dateAccepted",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="fecha aceptación",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="dateCopyrighted",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="fecha derechos de autor",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="dateSubmitted",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="fecha enviado",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="description",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="descripción",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="digitalFormat",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="formato digital",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="dynamic_identifier_cached",
            field=models.TextField(
                editable=False, null=True, verbose_name="identificador dinámico"
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="educationLevel",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="nivel educativo",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="extent",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="grado",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="format",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="formato",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="hasFormat",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="tiene formato",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="hasPart",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="tiene parte",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="hasVersion",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="tiene versión",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="identifier",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), size=None, verbose_name="identificador"
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="instructionalMethod",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="método de instrucción",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="isFormatOf",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="es formato de",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="isPartOf",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="es parte de",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="isReferencedBy",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="es referenciado por",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="isReplacedBy",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="es reemplazado por",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="isRequiredBy",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="es requerido por",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="isVersionOf",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="es versión de",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="issued",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="emitido",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="language",
            field=models.ManyToManyField(
                blank=True,
                related_name="language_resources",
                through="harvester.LanguageEquivalenceRelation",
                to="harvester.ContentResourceEquivalence",
                verbose_name="idioma",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="license",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="licencia",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="mediator",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="mediador",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="medium",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="medio",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="modified",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="modificado",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="provenance",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="procedencia",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="publisher",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="editor",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="references",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="referencias",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="relation",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="relación",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="replaces",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="reemplaza",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="requires",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="requiere",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="rights",
            field=models.ManyToManyField(
                blank=True,
                related_name="rights_resources",
                through="harvester.RightsEquivalenceRelation",
                to="harvester.ContentResourceEquivalence",
                verbose_name="derechos",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="rightsHolder",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="titular de los derechos",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="source",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="fuente",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="spatial",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="espacial",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="subject",
            field=models.ManyToManyField(
                blank=True,
                related_name="subject_resources",
                through="harvester.SubjectEquivalenceRelation",
                to="harvester.ContentResourceEquivalence",
                verbose_name="tema",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="tableOfContents",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="tabla de contenidos",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="temporal",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="temporal",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="title",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="título",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="topographicNumber",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="número topográfico",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="type",
            field=models.ManyToManyField(
                blank=True,
                related_name="type_resources",
                through="harvester.TypeEquivalenceRelation",
                to="harvester.ContentResourceEquivalence",
                verbose_name="tipo",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="valid",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(),
                null=True,
                size=None,
                verbose_name="válido",
            ),
        ),
        migrations.AlterField(
            model_name="contentresource",
            name="visible",
            field=models.BooleanField(
                default=True,
                help_text="Permite mostrar u ocultar un el recurso en el sitio.",
                verbose_name="visibilidad",
            ),
        ),
        migrations.AlterField(
            model_name="contentresourceequivalence",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="contentresourceequivalence",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="datasource",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="datasource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="dynamicidentifierconfig",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="dynamicidentifierconfig",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="equivalence",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="equivalence",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="historicalcollaborativecollection",
            name="created_at",
            field=models.DateTimeField(
                blank=True, editable=False, verbose_name="creado el"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcollaborativecollection",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="dueño",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcollaborativecollection",
            name="updated_at",
            field=models.DateTimeField(
                blank=True, editable=False, verbose_name="actualizado el"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcollection",
            name="created_at",
            field=models.DateTimeField(
                blank=True, editable=False, verbose_name="creado el"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcollection",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="dueño",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcollection",
            name="updated_at",
            field=models.DateTimeField(
                blank=True, editable=False, verbose_name="actualizado el"
            ),
        ),
        migrations.AlterField(
            model_name="promotedcontentresource",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="promotedcontentresource",
            name="priority",
            field=models.PositiveSmallIntegerField(
                help_text="Especifica la prioridad de este Recurso. Números menores se muestran primero en los listados.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1000),
                ],
                verbose_name="prioridad",
            ),
        ),
        migrations.AlterField(
            model_name="promotedcontentresource",
            name="resource",
            field=models.OneToOneField(
                limit_choices_to={"sets__visible": True, "visible": True},
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="harvester.ContentResource",
                verbose_name="recurso",
            ),
        ),
        migrations.AlterField(
            model_name="promotedcontentresource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="review",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="autor",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ],
                verbose_name="calificación",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="harvester.ContentResource",
                verbose_name="recurso",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="set",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="set",
            name="data_source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="harvester.DataSource",
                verbose_name="fuente de datos",
            ),
        ),
        migrations.AlterField(
            model_name="set",
            name="description",
            field=resources.fields.WysiwygField(
                blank=True, default="", verbose_name="descripción"
            ),
        ),
        migrations.AlterField(
            model_name="set",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="setandresource",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="setandresource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="sharedresource",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="sharedresource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
        migrations.AlterField(
            model_name="sharedresourceuser",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creado el"),
        ),
        migrations.AlterField(
            model_name="sharedresourceuser",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="actualizado el"),
        ),
    ]
