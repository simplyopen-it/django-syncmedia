# -*- coding: utf-8 -*-
from logging import getLogger

from django.contrib import admin
from .models import Host

logger = getLogger("syncmedia.admin")


class HostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'hostname',
        'url',
        'port',
        'username',
    )
    list_editable = (
        'hostname',
        'url',
        'port',
        'username',
    )
admin.site.register(Host, HostAdmin)
