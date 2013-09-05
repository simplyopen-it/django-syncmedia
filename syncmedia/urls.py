# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from syncmedia.views import SyncKeys, SyncMediaView

urlpatterns = patterns(
    '',
    url(r'^sync-command', SyncMediaView.as_view(), name="sync_media"),
    url(r'^', SyncKeys.as_view(), name="sync"),
)
