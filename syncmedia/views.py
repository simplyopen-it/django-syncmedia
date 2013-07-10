# -*- coding: utf-8 -*-
from django.utils.log import getLogger
from django.contrib.aderit.generic_utils.views import GenericProtectedView
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from syncmedia.models import Host

from socket import gethostname
import os
import pwd

logger = getLogger('syncmedia.views')

class SyncKeys(GenericProtectedView):
    use_login_required_decorator = False

    def post(self, request, *args, **kwargs):
        hid = request.POST.get('id')
        hurl = request.META.get('SERVER_NAME')
        if not Host.objects.filter(url=hurl).exists():
            logger.warning("Invalid sync post received from: %s; exiting", hurl)
            return HttpResponseRedirect('/')
        try:
            host = Host.objects.get(id=hid)
        except ObjectDoesNotExist:
            logger.warning("Invalid sync post received; id = %s", hid)
        else:
            curr_host = Host.objects.get_this()
            auth_keys = open(
                os.path.join(pwd.getpwnam(curr_host.username).pw_dir, ".ssh", "authorized_keys"),
                'a')
            try:
                auth_keys.write(host.pubkey)
            except Exception, e:
                logger.warning(e)
                raise e
            finally:
                auth_keys.close()
        return HttpResponseRedirect('/')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(SyncKeys, self).dispatch(*args, **kwargs)
