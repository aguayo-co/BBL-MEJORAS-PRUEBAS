from django.utils.translation import gettext_lazy as _


DUBLIN_CORE_DEFAULT_ASSOCIATION = [
    ("abstract", "abstract"),
    ("accessRights", "accessRights"),
    ("accrualMethod", "accrualMethod"),
    ("accrualPeriodicity", "accrualPeriodicity"),
    ("accrualPolicy", "accrualPolicy"),
    ("alternative", "alternative"),
    ("audience", "audience"),
    ("available", "available"),
    ("bibliographicCitation", "bibliographicCitation"),
    ("conformsTo", "conformsTo"),
    ("contributor", "contributor"),
    ("coverage", "coverage"),
    ("created", "created"),
    ("creator", "creator"),
    ("date", "date"),
    ("dateAccepted", "dateAccepted"),
    ("dateCopyrighted", "dateCopyrighted"),
    ("dateSubmitted", "dateSubmitted"),
    ("description", "description"),
    ("educationLevel", "educationLevel"),
    ("extent", "extent"),
    ("format", "format"),
    ("hasFormat", "hasFormat"),
    ("hasPart", "hasPart"),
    ("hasVersion", "hasVersion"),
    ("identifier", "identifier"),
    ("instructionalMethod", "instructionalMethod"),
    ("isFormatOf", "isFormatOf"),
    ("isPartOf", "isPartOf"),
    ("isReferencedBy", "isReferencedBy"),
    ("isReplacedBy", "isReplacedBy"),
    ("isRequiredBy", "isRequiredBy"),
    ("isVersionOf", "isVersionOf"),
    ("issued", "issued"),
    ("language", "language"),
    ("license", "license"),
    ("mediator", "mediator"),
    ("medium", "medium"),
    ("modified", "modified"),
    ("provenance", "provenance"),
    ("publisher", "publisher"),
    ("references", "references"),
    ("relation", "relation"),
    ("replaces", "replaces"),
    ("requires", "requires"),
    ("rights", "rights"),
    ("rightsHolder", "rightsHolder"),
    ("source", "source"),
    ("spatial", "spatial"),
    ("subject", "subject"),
    ("tableOfContents", "tableOfContents"),
    ("temporal", "temporal"),
    ("title", "title"),
    ("type", "type"),
    ("valid", "valid"),
]

DUBLIN_CORE_DEFAULT_ASSOCIATION_INITIAL = {
    "abstract": "abstract",
    "accessRights": "accessRights",
    "accrualMethod": "accrualMethod",
    "accrualPeriodicity": "accrualPeriodicity",
    "accrualPolicy": "accrualPolicy",
    "alternative": "alternative",
    "audience": "audience",
    "available": "available",
    "bibliographicCitation": "bibliographicCitation",
    "conformsTo": "conformsTo",
    "contributor": "contributor",
    "coverage": "coverage",
    "created": "created",
    "creator": "creator",
    "date": "date",
    "dateAccepted": "dateAccepted",
    "dateCopyrighted": "dateCopyrighted",
    "dateSubmitted": "dateSubmitted",
    "description": "description",
    "educationLevel": "educationLevel",
    "extent": "extent",
    "format": "format",
    "hasFormat": "hasFormat",
    "hasPart": "hasPart",
    "hasVersion": "hasVersion",
    "identifier": "identifier",
    "instructionalMethod": "instructionalMethod",
    "isFormatOf": "isFormatOf",
    "isPartOf": "isPartOf",
    "isReferencedBy": "isReferencedBy",
    "isReplacedBy": "isReplacedBy",
    "isRequiredBy": "isRequiredBy",
    "isVersionOf": "isVersionOf",
    "issued": "issued",
    "language": "language",
    "license": "license",
    "mediator": "mediator",
    "medium": "medium",
    "modified": "modified",
    "provenance": "provenance",
    "publisher": "publisher",
    "references": "references",
    "relation": "relation",
    "replaces": "replaces",
    "requires": "requires",
    "rights": "rights",
    "rightsHolder": "rightsHolder",
    "source": "source",
    "spatial": "spatial",
    "subject": "subject",
    "tableOfContents": "tableOfContents",
    "temporal": "temporal",
    "title": "title",
    "type": "type",
    "valid": "valid",
}

MARC_XML_DEFAULT_ASSOCIATION_INITIAL = {
    "contributor": "700,710,711,720$$$$",
    "creator": "100,110,111$$$$",
    "coverage": "651,662,751,752$$$$",
    "date": "007-010$$$$|260$c,g$$$",
    "description": "500-599$$$$",
    "format": "340$$$$|856$q$$$",
    "identifier": "020,022,024$a$$$|856$u$$$",
    "language": "008$$$$|035-037$$$$|041$a,b,d$$$|546$$$$",
    "publisher": "260$a,b$$$",
    "rights": "506,540$$$$",
    "subject": "600,610,611,630,650,653$$$$",
    "type": "655$$$$",
    "title": "245$a,b$1$$|246$a,b$1,3$0-8$",
}