# -*- coding: utf-8 -*-
import getpass
import sys
import os

from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils.log import getLogger
from syncmedia.models import Host
from socket import getfqdn

logger = getLogger("syncmedia.sync_media")


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-u', '--username', dest='username', default=None,
                    help='Name of the login user'),
        make_option('-k', '--keypath', dest='keypath', default=None,
                    help='path to the RSA public key'),
        make_option('-p', '--port', dest='port', default=None,
                    help='ssh port'),
        make_option('-i', '--interactive', dest='interactive', default=False,
                     help='make process interactive'),
    )

    help = "Rsync of media files with other host running the same application"
    synopsis = "init|unregister|push|pull [-u USERNAME|--username=USERNAME] [-k KEYPATH|--keypath=KEYPATH] [-p PORT|--port=PORT] [-i|--interactive]"

    def handle(self, *args, **options):
        if len(args) < 1:
            self.stdout.write("./run.py sync_media %s" % Command.synopsis)
            sys.exit(1)
        action = args[0]
        username = options.get('username', None)
        keypath = options.get('keypath', None)
        port = options.get('port', None)
        interactive = options.get('interactive', False)
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
                            self.stdout.write("Invalid or Empty Port: using default (22).\n")
                            port = 22
                        break
            except KeyboardInterrupt:
                sys.stderr.write("\nOperation cancelled.\n")
                sys.exit(1)
        else: # Not interactive
            if username is None:
                # Use executing user
                username = getpass.getuser()
            if port is None:
                port = 22
        if not action:
            self.stderr.write(Command.help + "\n")
            sys.exit(1)
        elif action == 'init':
            host, created = Host.objects.initialize(username, port=port, key=keypath)
            if created:
                self.stdout.write("Created Host %s - %s\n" % (host.id, host.url))
            else:
                self.stdout.write("Updated Host %s - %s\n" % (host.id, host.url))
        elif action == 'unregister':
            url = Host.objects.unregister()
            self.stdout.write("Unregistered host %s\n" % url)
        elif action == 'push':
            url = getfqdn()
            try:
                host = Host.objects.get(url=url)
                ret = host.push() # TODO: consent to specify dirs from options
                self.stdout.write(repr(ret) + "\n")
            except ObjectDoesNotExist:
                raise RuntimeError("Host %s is not registered, try to call 'syncmedia init' first",
                                   url)
        elif action == 'pull':
            url = getfqdn()
            try:
                host = Host.objects.get(url=url)
                ret = host.pull() # TODO: consent to specify a preferred host from options
                self.stdout.write(repr(ret) + "\n")
            except ObjectDoesNotExist:
                raise RuntimeError("Host %s is not registered, try to call 'syncmedia init' first",
                                   url)
        else:
            self.stdout.write("./run.py sync_media %s\n" % Command.synopsis)
            sys.exit(1)
        sys.exit(os.EX_OK)
