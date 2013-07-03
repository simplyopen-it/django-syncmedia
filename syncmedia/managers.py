# -*- coding: utf-8 -*-
import os
import pwd
import httplib
import urllib
import socket

from django.db import models
from socket import gethostname, getfqdn
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.log import getLogger

logger = getLogger("syncmedia.manager")


class HostManager(models.Manager):

    def _notify(self, this, host, proto='http'):
        if proto == 'http':
            conn = httplib.HTTPConnection(host.url)
        elif proto == 'https':
            conn = httplib.HTTPSConnection(host.url)
        params = urllib.urlencode({'id': this.id})
        conn.request("POST", reverse('sync'), params)
        response = conn.getresponse()
        logger.debug('response: %s', response)
        if response.status == 301:
            host = response.getheader('location').slpit('://')
            return self._notify(this, host[1], proto=host[0])
        return True

    def initialize(self, user, port=22, key=None):
        ''' Initialize a new syncronizing host.
        It reads all others host's public keys from the database and
        write them in authorized_keys; then it save it's own key on
        the database and notify others so that they can update their
        authorized_keys too.

        Parameters
        ----------
        user: the username to make ssh connection with.
        port: ssh port
        key: public RSA key or path to a file containing it.

        Returns
        -------
        a tuple of (object, created), where created is a boolean
        specifying whether an object was created.

        '''
        hostname = gethostname()
        url = getfqdn()
        home_ssh = os.path.join(pwd.getpwnam(user).pw_dir, '.ssh')
        if key is None:
            key = os.path.join(home_ssh, 'id_rsa.pub')
        if os.path.isfile(key):
            # It's a file containinge (hopefully) the key
            key_fd = open(key, 'r')
            try:
                rsa_pub = key_fd.read()
            finally:
                key_fd.close()
        elif key.startswith('ssh-rsa'):
            # It's the key
            rsa_pub = key
        else:
            raise ValueError(
                "'key' must be a valid RSA public key or a file that \
                contains one; '%s' given" % key)
        # Get other Host's keys
        pubkeys = [elem.get('pubkey') for elem in self.all().values('pubkey')]
        # write keys to authorized_keys
        auth_fd = open(os.path.join(home_ssh, "authorized_keys"), 'a')
        try:
            for pubkey in pubkeys:
                auth_fd.write("%s" % pubkey)
        finally:
            auth_fd.close()
        # Create the new host
        try:
            this_host = self.get(url=url)
            this_host.hostname = hostname
            this_host.url = url
            this_host.port = port
            this_host.username = user
            this_host.pubkey = rsa_pub
            created = False
        except ObjectDoesNotExist:
            this_host = self.model(
                hostname=hostname,
                url=url,
                port=port,
                username=user, pubkey=rsa_pub)
            created = True
        finally:
            this_host.save()
        # Notify other Hosts
        hosts = self.all().exclude(url=this_host.url)
        for host in hosts:
            self._notify(this_host, host)
        return (this_host, created)

    def get_this(self):
        ''' Return the current Host '''
        url = getfqdn()
        try:
            return self.get(url=url)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("Host %s not registered" % url)

    def unregister(self, url=None):
        ''' Unregister an Host from syncronization.

        Parameters
        ----------
        url: The url of the host to unregister; if None the host
        calling this method is removed from Host.

        Return
        ------
        The url of the unregistered host

        '''
        if url is None:
            host = self.get_this()
            url = host.url
            host.delete()
        else:
            self.get(url=url).delete()
        return url