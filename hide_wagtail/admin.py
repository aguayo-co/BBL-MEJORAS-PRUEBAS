from django.contrib import admin
from wagtail.documents.models import Document
from wagtail.images.models import Image
from taggit.admin import Tag

admin.site.unregister(Document)
admin.site.unregister(Image)
admin.site.unregister(Tag)
