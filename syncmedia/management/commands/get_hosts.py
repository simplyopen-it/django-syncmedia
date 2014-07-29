from syncmedia.models import Host
from django.core.management.base import BaseCommand
from csv import writer
from sys import stdout


class Command(BaseCommand):
    help = 'Print all Hosts from db.\n'

    def handle(self, *args, **options): # pylint: disable=W0613
        csvf = writer(stdout)
        csvf.writerow(['username', 'password', 'hostname', 'url', 'port'])
        for i in Host.objects.all():
            csvf.writerow([i.username, i.password,
                           i.hostname, i.url, i.port ])
