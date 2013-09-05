# -*- coding: utf-8 -*-

__version__ = "0.1.5"

#################################################
# Commands to reload different kind of services #
#################################################
from django.conf import settings

GUNICONR_WSGI="""kill -HUP $(cat /var/run/gunicorn/%s.wsgi.pid)""" % \
    settings.PROJECT_NAME

# TODO: define other webserver's reload commands