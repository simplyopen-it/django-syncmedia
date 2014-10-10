import os
from django.conf import settings

def abspath(path):
    ret = os.path.abspath(path)
    if path.endswith(os.path.sep):
        ret += os.path.sep
    return ret

def get_auth_keys():
    return abspath(os.path.join(os.path.dirname(settings.PATH_RSA), 'authorized_keys'))

def get_id_rsa():
    return settings.PATH_RSA
