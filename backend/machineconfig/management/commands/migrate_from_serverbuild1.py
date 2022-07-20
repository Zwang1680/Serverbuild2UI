from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from machineconfig.models import Machine

from machineconfig.models import Site
from machineconfig.models import Hostname
from machineconfig.models import PuppetMachine
from machineconfig.models import NetworkDevice
from machineconfig.models import NetworkInterface
from machineconfig.models import NetworkInterfaceConfiguration

class IntentionalAbortError(Exception):
    pass

class Command(BaseCommand):
    help = '''Migrate the Machine class from ServerBuild 1.x to ServerBuild 2.x Database'''

    def add_arguments(self, parser):
        parser.add_argument('--destructive', action='store_true', default=False, help='Take DESTRUCTIVE ACTION (save to database)')

    def process_one_machine(self, machine, destructive=False):
        try:
            site = Site.objects.filter(code__iexact=machine.site).get()
        except Site.DoesNotExist as ex:
            self.stderr.write(self.style.ERROR(f'ERROR: No Site object found for Machine.site={machine.site}'))
            self.stderr.write(self.style.ERROR(f'ERROR: Please manually create Site "{machine.site}" first!!!'))
            return

        # look up new NetworkDevice model using the Machine.mac field
        # check if it has already been migrated, and skip it
        queryset = NetworkInterface.objects.filter(mac__iexact=machine.mac)
        count = queryset.count()
        if count >= 1:
            self.stdout.write(self.style.SUCCESS(f'ALREADY IMPORTED, SKIP Machine(mac={machine.mac})'))
            return

        # BEGIN TRANSACTION ... COMMIT / ABORT
        with transaction.atomic():
            # NetworkDevice
            networkdevice = NetworkDevice(site=site)
            networkdevice.save()

            # PuppetMachine
            puppetmachine = PuppetMachine(networkdevice=networkdevice)
            puppetmachine.operatingsystem = f'{machine.ostype}-{machine.osversion}-{machine.arch}'
            puppetmachine.partitionscheme = machine.partition
            puppetmachine.partitionscheme_custom = machine.partition_custom
            puppetmachine.boot_mode = machine.boot_mode
            puppetmachine.save()

            # NetworkInterface.mac
            netinterface = NetworkInterface(networkdevice=networkdevice)
            netinterface.mac = machine.mac
            netinterface.save()

            # NetworkInterfaceConfiguration.ipaddress
            ipaddress = '' if machine.netconf == 'dhcp' else machine.ipaddress
            ipaddress = '' if ipaddress is None else ipaddress
            nic = NetworkInterfaceConfiguration(networkinterface=netinterface)
            nic.ipaddress = ipaddress
            nic.save()

            # NetworkInterfaceConfiguration.hostname_set[]
            hostname = Hostname(networkinterfaceconfiguration=nic)
            hostname.hostname = machine.hostname
            hostname.save()

            # ABORT in non-destructive mode
            if not destructive:
                raise IntentionalAbortError('Intentional abort on --destructive=False')

    def handle(self, *args, **options):
        for machine in Machine.objects.all():
            print(f'BEGIN processing Machine(pk={machine.pk})')

            try:
                destructive = options.get('destructive', False)
                self.process_one_machine(machine, destructive=destructive)
            except IntentionalAbortError as ex:
                pass

            self.stdout.write(self.style.SUCCESS(f'FINISH processing Machine(pk={machine.pk})'))
