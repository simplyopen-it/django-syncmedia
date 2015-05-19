# -*- coding: utf-8 -*-
from django.utils.log import getLogger
# from django.contrib.aderit.generic_utils.views import GenericProtectedView
from simplyopen.views import GenericProtectedView
from django.views.generic import View
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from syncmedia.models import Host
from django.conf import settings
from syncmedia import authorized_keys
import os
import pwd

logger = getLogger('syncmedia.views')


class StaffProtectedView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff or request.user.is_active and request.user.is_superuser:
            return super(StaffProtectedView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff or request.user.is_active and request.user.is_superuser:
            return super(StaffProtectedView, self).post(request, *args, **kwargs)
        else:
            raise Http404


class SyncKeys(GenericProtectedView):
    use_login_required_decorator = False

    def post(self, request, *args, **kwargs): # pylint: disable=W0613
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
            auth_path = os.path.join(pwd.getpwnam(curr_host.username).pw_dir,
                                           ".ssh", "authorized_keys")
            authorized_keys.add_key(host.pubkey, auth_path)

        return HttpResponseRedirect('/')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(SyncKeys, self).dispatch(*args, **kwargs)


class SyncMediaView(StaffProtectedView, GenericProtectedView):
    use_login_required_decorator = True

    def get(self, request, *args, **kwargs):
        if request.GET.get('type') and request.GET.get('kill'):
            ex_type = request.GET.get('type')
            host = Host.objects.get_this()
            func = getattr(host, ex_type, 'push')
            kill = request.GET.get('kill') == 'True'
            func(sync_dirs=getattr(settings, 'SYNCHRO_DIRS', 'locale/'), kill=kill)
            if kill:
                host.kill()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('admin:index')))
