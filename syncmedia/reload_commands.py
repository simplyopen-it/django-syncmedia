# -*- coding: utf-8 -*-

from django.conf import settings

GUNICORN_WSGI = """/bin/ps -o pid --ppid $(cat /var/run/gunicorn/%s.wsgi.pid) --noheaders | /usr/bin/xargs -I{} /bin/kill -HUP {}""" % settings.PROJECT_NAME
