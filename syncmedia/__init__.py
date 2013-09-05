# -*- coding: utf-8 -*-

__version__ = "0.1.6"

#################################################
# Commands to reload different kind of services #
#################################################
from django.conf import settings

GUNICORN_WSGI="ps --ppid $(cat /var/run/gunicorn/%s.wsgi.pid) | grep python | awk '{ print $1 }' | xargs kill -HUP" % settings.PROJECT_NAME

# TODO: define other webserver's reload commands