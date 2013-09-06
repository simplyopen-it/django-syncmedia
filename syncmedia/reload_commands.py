# -*- coding: utf-8 -*-

from django.conf import settings

GUNICORN_WSGI="""ps --ppid $(cat /var/run/gunicorn/%s.wsgi.pid) | grep python | cut -d" " -f2 | xargs -I{} kill -HUP {}""" % settings.PROJECT_NAME
