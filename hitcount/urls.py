# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path
from hitcount.views import HitCountJSONView

app_name = "hitcount"

urlpatterns = [path(r"^hit/ajax/$", HitCountJSONView.as_view(), name="hit_ajax")]
