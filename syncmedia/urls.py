# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.admin import site
from syncmedia.views import SyncKeys, SyncMediaView

urlpatterns = [
    url(r'^sync-command', site.admin_view(SyncMediaView.as_view()), name="sync_media"),
    url(r'^', SyncKeys.as_view(), name="sync"),
]
