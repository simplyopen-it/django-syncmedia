# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.log import getLogger
from syncmedia.models import Host

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


