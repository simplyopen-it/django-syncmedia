# -*- coding: utf-8 -*-
# pylint: disable=E1120
from django.conf.urls import patterns, url
from django.contrib.admin import site
from syncmedia.views import SyncKeys, SyncMediaView

urlpatterns = patterns(
    '',
    url(r'^sync-command', site.admin_view(SyncMediaView.as_view()), name="sync_media"),
    url(r'^', SyncKeys.as_view(), name="sync"),
)
