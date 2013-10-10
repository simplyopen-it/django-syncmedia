from django.core.management.base import BaseCommand
import subprocess
import time
import sys
import os

class Command(BaseCommand):
    help = 'Reload all Gunicorn workers with sudo.\n'
    synopsis = "nothing..."
    
    def handle(self, *args, **options):
        try:
            ret = subprocess.call(['/usr/bin/sudo', '-n', '/etc/init.d/gunicorn', 'reload'])
            if ret == 0:
                self.stdout.write("SYNCMEDIA: reloaded Gunicorn at %s\n" % (time.ctime()))
            else:
                self.stdout.write("SYNCMEDIA error reloading Gunicorn at %s\n" % (time.ctime()))
            sys.exit(ret)
        except subprocess.CalledProcessError, e:
            self.stdout.write("SYNCMEDIA error reloading Gunicorn at %s\n" % (time.ctime()))
            self.stdout.write("SYNCMEDIA error: %s\n" % e)
            sys.exit(e.errno)
        except OSError, e:
            self.stdout.write("SYNCMEDIA error reloading Gunicorn at %s\n" % (time.ctime()))
            self.stdout.write("SYNCMEDIA error: %s\n" % e)
            sys.exit(e.errno)
            
