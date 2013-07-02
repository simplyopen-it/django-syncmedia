from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from syncmedia.models import Host
from socket import gethostname, getfqdn
import subprocess
from django.utils.log import getLogger

logger = getLogger("syncmedia.syncmedia_push")

import os
import pwd

SYNCHRO_DIRS = getattr(settings, "SYNCHRO_DIRS", ['media/','hidden/'])
PROJECT_PATH = getattr(settings, "PROJECT_PATH", '/var/www/***REMOVED***')


class Command(BaseCommand):

    help = 'Command to manage the synchronization of all media to all Hosts'

    def handle(self, *args, **options):
        curr_hostname = gethostname()
        try:
            curr_host = Host.objects.get(hostname=curr_hostname)
        except ObjectDoesNotExist:
            logger.warning('Host %s not registered yet', curr_hostname)
            return False
        for host in Host.objects.all():
            if host.hostname != gethostname():
                for sdir in SYNCHRO_DIRS:
                    to_rsync = os.path.join(PROJECT_PATH, sdir)
                    path_rsa = getattr(
                        settings, "PATH_RSA",
                        os.path.join(pwd.getpwnam(curr_host.username).pw_dir, ".ssh", "id_rsa"))
                    params = [
                        '/usr/bin/rsync',
                        '-r',
                        '--rsh="ssh -p%s -i %s"' % (host.port, path_rsa),
                        to_rsync,
                        '%s@%s:%s' % (host.username, host.url, to_rsync),
                    ]
                    try:
                        out = subprocess.call(params)
                        logger.debug("%s returned %s", " ".join(params), out)
                    except Exception, e:
                        logger.error(e)
                        self.stderr.write(e.message)
                        continue
                    if out == 0:
                        self.stdout.write('Successfully synced %s to %s\n' % (sdir, host))
		    else :
                        self.stdout.write(
                            'Error syncing %s to %s, return code was %s\n' % (sdir, host, out))
        return True



