import os
import signal
import psutil
import time
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Reload all Gunicorn workers.\n'
    synopsis = "nothing..."
    
    def check_pid_running(self, pid, psignal=signal.SIG_DFL):
        '''Check For the existence of a unix pid.
        '''
        try:
            os.kill(pid, psignal)
        except OSError:
            return False
        else:
            return True

    def exit_with_code(self, exit_code=os.EX_OK, lock_file=None, message=None):
        if not lock_file is None and os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except Exception:
                pass
        if not message is None:
            self.stdout.write(message)
        sys.exit(exit_code)
        
    def handle(self, *args, **options):
        lock_file = os.path.join("/tmp", str().join([settings.PROJECT_NAME, "_reload.lock"]))
        if os.path.exists(lock_file):
            self.exit_with_code(1, None, 'Only one script can run at once. Script is locked with %s\n' % (lock_file))

        try:
            lock = open(lock_file, 'w')
            lock.write("")
        except Exception, e:
            self.exit_with_code(e.errno, None, "ERROR: impossible create lock file %s - %s !\n" % (lock_file, e))

        pidfile = os.path.join("/var/run/gunicorn/", str().join([settings.PROJECT_NAME, ".wsgi.pid"]))
        if os.path.isfile(pidfile):
            parent_pid = int(file(pidfile, 'r').readlines()[0])
            try:
                p = psutil.Process(parent_pid)
            except psutil.NoSuchProcess:
                self.exit_with_code(e.errno, lock_file, "ERROR: pid %s from pidfile %s not running!\n" % (pidfile, parent_pid))

            child_pid = p.get_children(recursive=True)
            for pid in child_pid:
                if self.check_pid_running(pid.pid):
                    self.stdout.write("SIGHUP on pid %s at %s\n" % (pid.pid, time.ctime()))
                    self.stdout.flush()
                    self.check_pid_running(pid.pid, signal.SIGHUP)
                    time.sleep(3)
                else:
                    self.stdout.write("WARNING: pid %s is not running or executed under another user!\n" % (pid.pid))
                    self.stdout.flush()
        else:
            self.exit_with_code(1, lock_file, "ERROR: pidfile %s not found!\n" % (pidfile))

        self.exit_with_code(os.EX_OK, lock_file, "SUCCESS: all workers restarted!\n")
                
