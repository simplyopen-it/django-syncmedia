# -*- coding: utf-8 -*-

#from django.conf import settings

''' KILL HUP CHILD '''
#GUNICORN_WSGI = """/bin/ps -o pid --ppid $(cat /var/run/gunicorn/%s.wsgi.pid) --noheaders | /usr/bin/xargs -I{} /bin/kill -HUP {}""" % settings.PROJECT_NAME

''' KILL HUP CHILD WAITING FOR EACH ONE '''
#GUNICORN_WSGI = """/bin/cd %s && /usr/bin/python run.py reload_gunicorn_child""" % settings.PROJECT_PATH

''' KILL HUP MASTER WITH SUDO '''
GUNICORN_WSGI = """/usr/bin/sudo /etc/init.d/gunicorn reload"""

''' KILL HUP MASTER WITH SUDO AND RUN.PY'''
#GUNICORN_WSGI = """/bin/cd %s && /usr/bin/python run.py reload_gunicorn"""
