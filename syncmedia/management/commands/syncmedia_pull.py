from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from syncmedia.models import Host
from socket import gethostname, getfqdn
import subprocess
from django.utils.log import getLogger

logger = getLogger("syncmedia.syncmedia_pull")

import os
import pwd

SYNCHRO_DIRS = getattr(settings, "SYNCHRO_DIRS", ['media/','hidden/'])
PROJECT_PATH = getattr(settings, "PROJECT_PATH", '/var/www/***REMOVED***')


class Command(BaseCommand):

    help = 'Command to manage the synchronization of all media to all Hosts'

    def handle(self, *args, **options):
        host = Host.objects.exclude(hostname=gethostname(), url=getfqdn())[0] # First different Host
        curr_hostname = gethostname()
        try:
            curr_host = Host.objects.get(hostname=curr_hostname)
        except ObjectDoesNotExist:
            logger.warning('Host %s not registered yet', curr_hostname)
            return False
        for sdir in SYNCHRO_DIRS:
            to_rsync = os.path.join(PROJECT_PATH, sdir)
            path_rsa = getattr(
                settings, "PATH_RSA",
                os.path.join(pwd.getpwnam(curr_host.username).pw_dir, ".ssh", "id_rsa"))
            try:
                out = subprocess.call([
                    '/usr/bin/rsync',
                    '-r',
                    '--rsh="ssh -p%s -i %s"' % (host.port, path_rsa),
                    '%s@%s:%s' % (host.username, host.url, to_rsync),
                    to_rsync,
                ])
            except Exception, e:
                logger.error(e)
                self.stderr.write(e.message)
                continue
            self.stdout.write('Successfully synced %s to %s\n' % (sdir, host))
        return True




