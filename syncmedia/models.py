# -*- coding: utf-8 -*-
import os
import pwd
import subprocess
from threading import Thread
from syncmedia import managers
from syncmedia import reload_commands
from syncmedia.utils import abspath
from django.db import models
from django.utils.log import getLogger
from django.conf import settings
from django_extensions.db.fields.json import JSONField
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist


logger = getLogger("syncmedia.models")
SYNC_DIRS = getattr(settings, "SYNCHRO_DIRS", [])
MODELS_SYNC = getattr(settings, 'MODELS_SYNC', {})
PROJECT_PATH = getattr(settings, "PROJECT_PATH")
COM_RELOAD = getattr(settings, "COMM_RELOAD", reload_commands.GUNICORN_WSGI)
DEF_TIMEOUT = 10 # ssh timeout in seconds


class Host(models.Model):
    hostname = models.CharField(max_length=256, unique=True)
    url = models.CharField(max_length=256, unique=True)
    port = models.IntegerField(max_length=40, default=9922)
    username = models.CharField(max_length=256, blank=True, null=True)
    pubkey = models.CharField(max_length=512)
    sync_dirs = JSONField(blank=True, null=True, default='[]') # pylint: disable=E1120,E1123
    root_path = models.CharField(max_length=512, blank=True, null=True, default=os.getcwd())

    objects = managers.HostManager()

    def __unicode__(self):
        return str(" ").join([self.hostname, self.url])

    def clean_fields(self, exclude=None):
        errors = {}
        try:
            super(Host, self).clean_fields(exclude=exclude)
        except ValueError as e:
            errors = e.message_dict
        if self.root_path and not os.path.isabs(self.root_path):
            errors['root_path'] = ['root_path must be an absolute path.']
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Host, self).save(*args, **kwargs)

    @property
    def path_rsa(self):
        return getattr(
            settings, "PATH_RSA",
            os.path.join(pwd.getpwnam(self.username).pw_dir, ".ssh", "id_rsa"))

    def kill(self, host=None, timeout=DEF_TIMEOUT):
        shell = False
        if host is None:
            command = ['''%s''' % COM_RELOAD]
            # This is needed to have the subprocess accept command pipelines
            shell = True
        else:
            command = [
                '/usr/bin/ssh',
                '-p %s' % host.port,
                '-i %s' % self.path_rsa,
                "-o StrictHostKeyChecking=no",
                "-o ConnectTimeout=%s" % timeout,
                '%s@%s' % (host.username, host.url),
                """%s""" % COM_RELOAD,
            ]
        logger.debug("%s", " ".join(command))
        try:
            ret = subprocess.call(command, shell=shell)
        except Exception, e:
            logger.error(e)
            ret = e.errno
        if ret == 0:
            logger.info("kill of %s SUCCEDED", host)
        else:
            logger.warning("kill of %s FAILED, retuned %s",
                           host, ret)
        return ret

    def push(self, sync_dirs=None, timeout=DEF_TIMEOUT, kill=False,
             exclude=".*"):
        ''' Run _push() in a separate thread, to be called from django
        modules to avoid waiting syncronization when uploading a file.
        '''
        thread = Thread(
            target=self._push,
            args=(sync_dirs, timeout, kill, exclude))
        thread.start()

    def command_push(self, sync_dirs=None, timeout=DEF_TIMEOUT,
                     kill=False, exclude=".*"):
        ''' Wrapper method to call _push() from a management command
        script.
        '''
        return self._push(
            sync_dirs=sync_dirs,
            timeout=timeout, kill=kill, exclude=exclude)

    def _push(self, sync_dirs=None, timeout=DEF_TIMEOUT, kill=False,
              exclude=".*"):
        ''' Rsync push to others hosts.

        Parameters
        ----------
        sync_dirs: list of directory to sync (path a relative to
            PROJECT_PATH).
        timeout: timeout in seconds for ssh connection.
        kill: if True call a remote command to restart the server.
        exclude: exclude parameter to pass to rsync (default: exclude
            hidden files).

        Returns
        -------
        a dictionary with host's urls keys and couples (dirname, bool)
            for each succeded or failed sync.

        '''
        if sync_dirs is None:
            sync_dirs = SYNC_DIRS
        hosts = Host.objects.all().exclude(url=self.url)
        ret = {}
        for host in hosts:
            # Select only directories allowed for this host
            to_sync = set(sync_dirs)
            if host.sync_dirs:
                to_sync = set(host.sync_dirs).intersection(to_sync)
            ret[host.url] = []
            for sync_dir in to_sync:
                src_path = os.path.join(self.root_path, sync_dir) if self.root_path else abspath(sync_dir)
                dest_path = os.path.join(host.root_path, sync_dir) if host.root_path else abspath(sync_dir)
                rsync_call = [
                    '/usr/bin/rsync',
                    '-a',
                    '-z',
                    '--ignore-existing',
                    '-e',
                    "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=%s -p %s -i %s" % \
                    (timeout, host.port, self.path_rsa),
                    src_path,
                    "%s@%s:%s" % (host.username, host.url, dest_path),
                ]
                if exclude:
                    rsync_call.insert(1, '''--exclude=%s''' % exclude)
                logger.debug("%s", " ".join(rsync_call))
                try:
                    out = subprocess.call(rsync_call)
                except Exception, e:
                    logger.error(e)
                    continue
                if out == 0:
                    logger.info("push of %s to %s SUCCEDED", sync_dir, host)
                    ret[host.url].append( (sync_dir, True) )
                    # Eventually send a command to restart remote host
                    if kill:
                        self.kill(host, timeout)
                else:
                    logger.info("push of %s to %s FAILED", sync_dir, host)
                    ret[host.url].append( (sync_dir, False) )
        return ret

    def pull(self, host=None, sync_dirs=None, timeout=DEF_TIMEOUT,
             kill=False, exclude=".*"):
        ''' Run _pull() in a separate thread, to be called from django
        modules to avoid waiting syncronization when uploading a file.
        '''
        thread = Thread(
            target=self._pull,
            args=(host, sync_dirs, timeout, kill, exclude))
        thread.start()

    def command_pull(self, sync_dirs=None, timeout=DEF_TIMEOUT,
                     kill=False, exclude=".*"):
        ''' Wrapper method to call _pull() from a management command
        script.
        '''
        return self._pull(sync_dirs=sync_dirs, timeout=timeout,
                          kill=kill, exclude=exclude)

    def _pull(self, host=None, sync_dirs=None, timeout=DEF_TIMEOUT,
              kill=False, exclude=".*"):
        ''' Rsync pull to others hosts.

        Parameters
        ----------
        host: host to pull data from, if it's None a random one will
             be picked.
        sync_dirs: list of directory to sync (path a relative to
            PROJECT_PATH).
        timeout: timeout in seconds for ssh connection.
        kill: if True call a command to restart the local server.
        exclude: exclude parameter to pass to rsync (default: exclude
            hidden files).

        Returns
        -------
        A dictionaty with dirnames as keys and bools as values,
            indicating wether the rsync succeded or not.

        '''
        hosts = [host] if host is not None else Host.objects.all().exclude(url=self.url)
        if sync_dirs is None:
            sync_dirs = SYNC_DIRS
        ret = {}
        for host in hosts:
            # Select only directories allowed for this host
            to_sync = set(sync_dirs)
            if host.sync_dirs:
                to_sync = set(host.sync_dirs).intersection(to_sync)
            ret[host.url] = []
            for sync_dir in to_sync:
                src_path = os.path.join(host.root_path, sync_dir) if host.root_path else abspath(sync_dir)
                dest_path = os.path.join(self.root_path, sync_dir) if self.root_path else abspath(sync_dir)
                rsync_call = [
                    '/usr/bin/rsync',
                    '-a',
                    '-z',
                    '--ignore-existing',
                    '-e',
                    "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=%s -p %s -i %s" % \
                    (timeout, host.port, self.path_rsa),
                    "%s@%s:%s" % (host.username, host.url, src_path),
                    dest_path,
                ]
                if exclude:
                    rsync_call.insert(1, '''--exclude=%s''' % exclude)
                logger.debug("%s", " ".join(rsync_call))
                try:
                    out = subprocess.call(rsync_call)
                except Exception, e:
                    logger.error(e)
                    continue
                if out == 0:
                    logger.info("pull of %s from %s SUCCEDED", sync_dir, host)
                    ret[host.url].append( (sync_dir, True) )
                else:
                    logger.info("pull of %s from %s FAILED", sync_dir, host)
                    ret[host.url].append( (sync_dir, False) )
        if kill and any([result for _, result in ret.itervalues()]):
            self.kill() # Self kill! :D
        return ret


def sync(sender, **kw):
    key = '.'.join([sender.__module__, sender.__name__])
    if key in MODELS_SYNC.keys():
        kwargs = MODELS_SYNC[key]
        try:
            Host.objects.get_this().pull(**kwargs)
            Host.objects.get_this().push(**kwargs)
        except ObjectDoesNotExist, e:
            logger.error(e)
post_save.connect(sync)
