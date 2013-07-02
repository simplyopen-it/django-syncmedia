# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from syncmedia.views import SyncKeys

urlpatterns = patterns(
    '',
    url(r'^$', SyncKeys.as_view(), name="sync"),
)