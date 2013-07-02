import sys
from optparse import make_option

from syncmedia.models import Host
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from socket import gethostname, getfqdn
from django.utils.log import getLogger
import httplib
import urllib
import os
import stat
import pwd

logger = getLogger("syncmedia.syncmedia_initialize")

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--username', dest='username', default=None,
                    help='Specifies the username for the host.'),
        make_option('--keypath', dest='keypath', default=None,
                    help='Specifies the path to the RSA public key.'),
        make_option('--port', dest='port', default=None,
                    help='Specifies the port for the host.'),
        make_option('--interactive', dest='interactive', default=False,
                    help='Specifies if call in interactive mode'),
        )

    help = 'Used to create a new Host for Sync.\n'

    def handle(self, *args, **options):
        hostname = gethostname()
        url = getfqdn()
        username = options.get('username', None)
        keypath = options.get('keypath', None)
        port = options.get('port', None)
        interactive = options.get('interactive')

        if interactive:
            self.stdout.write("Interactive Mode Started ...\n")
            try:
                while 1:
                    if not username:
                        input_msg = 'Username'
                        username = raw_input(input_msg + ': ')
                        break
                while 1:
                    if not keypath:
                        input_msg = 'Public RSA key path'
                        keypath = raw_input(input_msg + ': ')
                        break
                while 1:
                    if not port:
                        input_msg = 'Port'
                        port = raw_input(input_msg + ': ')
                        if not port or not port.isdigit():
                            self.stdout.write("Invalid or Empty Port: using default.\n")
                            port = 9922
                        break
            except KeyboardInterrupt:
                sys.stderr.write("\nOperation cancelled.\n")
                sys.exit(1)
        # Write authorized_keys
        pubkeys = [elem.get('pubkey') for elem in Host.objects.all().values('pubkey')]
        auth_fd = os.open(
            os.path.join(pwd.getpwnam(username).pw_dir, ".ssh", "authorized_keys"),
            os.O_WRONLY | os.O_CREAT | os.O_APPEND,
            stat.S_IRUSR | stat.S_IWUSR)
        try:
            for pubkey in pubkeys:
                os.write(auth_fd, "%s\n" % pubkey)
            # auth_fd.writelines(pubkeys)
        except IOError, e:
            logger.warning(e)
            raise e
        except Exception, e:
            logger.warning(e)
            raise e
        finally:
            os.close(auth_fd)

        # Save new host
        try:
            key_fd = open(keypath, 'r')
            pubkey = key_fd.read()
        except IOError, e:
            pubkey = None
            logger.error(e)
            self.stderr.write(e.message)
        else:
            key_fd.close()
        logger.debug("hostname: %s", hostname)
        logger.debug("url: %s", url)
        logger.debug("port: %s", port)
        logger.debug("username: %s", username)
        logger.debug("keypath: %s", keypath)
        logger.debug("pubkey: %s", pubkey)
        if hostname and url and port and username and pubkey:
            try:
                nh, created = Host.objects.get_or_create(**{'url' : url})
                nh.hostname = hostname
                nh.url = url
                nh.port = port
                nh.username = username
                nh.pubkey = pubkey
                nh.save()
            except Exception, e:
                logger.error(e)
                self.stdout.write("Exception: %s.\nPlease retry" % e)
            else:
                self.stdout.write("Host '%s' Created Successfully.\n" % hostname)
                for i in Host.objects.all().exclude(id=nh.id, url=nh.url):
                    conn = httplib.HTTPConnection(i.url)
                    params = urllib.urlencode({'id': nh.id})
                    conn.request("POST", reverse('sync'), params)
                    response = conn.getresponse()
                    print response

        else:
            self.stdout.write("Please insert the required values.\nUsage: ./run.py syncmedia_initialize --username=xxxxx --keypath=xxxxx --port=000\nOr use the interactive mode with --interactive=True\n")
