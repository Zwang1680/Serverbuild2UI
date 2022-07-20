import re

from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.utils.timezone import make_aware
from django.dispatch import receiver
from django.db import models

from functools import cached_property
from urllib.parse import urlencode
from ipaddress import ip_address
from ipaddress import ip_network
import datetime
import requests
import json

def puppetdb_facts(hostname):
    '''
    Retrieve the Puppet Facts from PuppetDB for the given NetworkDevice

    @hostname: the Hostname to fetch from PuppetDB Facts Database
    @returns: dictionary (JSON Puppet Facts)
    '''
    print(f'QUERY PUPPETDB: hostname={hostname}')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    query = ["=", "certname", hostname, ]
    data = { 'query': json.dumps(query), }
    data = urlencode(data)
    # TODO FIXME: configurable PuppetDB URL
    url = 'http://puppetdb.lco.gtn:8080/pdb/query/v4/facts'
    response = requests.get(url, timeout=10, headers=headers, data=data)
    response.raise_for_status()
    return response.json()

class Site(models.Model):
    '''Database model which defines an LCO Site (Telescope or other)'''
    code = models.CharField(max_length=3, verbose_name='LCO Site Code', blank=False, unique=True)
    shortdescription = models.CharField(max_length=128, verbose_name='Short Description', blank=False)
    description = models.TextField(max_length=(128 * 1024), verbose_name='Description', blank=True)

    domain = models.CharField(max_length=64, verbose_name='Network Domain', blank=False, unique=True)
    networkip = models.GenericIPAddressField(verbose_name='Network IP Address', protocol='ipv4', unique=True)
    networkcidr = models.SmallIntegerField(verbose_name='Network CIDR', default=16)
    gateway = models.GenericIPAddressField(verbose_name='Default Gateway', protocol='ipv4')
    dnsservers = ArrayField(models.GenericIPAddressField(verbose_name='DNS Servers', protocol='ipv4'), default=list)
    # NOTE: implicit list of NTP servers in "ntpserver_set" member variable

    external_networkip = models.GenericIPAddressField(verbose_name='External Network IP Address', protocol='ipv4', default='0.0.0.0')
    external_networkcidr = models.SmallIntegerField(verbose_name='External Network CIDR', default=30)
    external_borderexternal = models.GenericIPAddressField(verbose_name='External Border Router IP Address', protocol='ipv4', default='0.0.0.0')
    external_borderuplink = models.GenericIPAddressField(verbose_name='External Border Router Next-Hop Uplink IP Address', protocol='ipv4', default='0.0.0.0')
    external_sitetositevpnip = models.GenericIPAddressField(verbose_name='IPSec VPN Backend IP Address', protocol='ipv4', default='0.0.0.0')

    latitude = models.FloatField(verbose_name='Latitude', blank=False, default=0.0)
    longitude = models.FloatField(verbose_name='Longitude', blank=False, default=0.0)
    elevation = models.FloatField(verbose_name='Elevation', blank=False, default=0.0)
    timezone = models.CharField(max_length=64, verbose_name='Timezone', blank=False, unique=False, default='Etc/UTC')
    restart_time = models.TimeField(verbose_name='Restart Time', blank=False, unique=False, default='00:00:00')

    mirrorbase = models.URLField(max_length=1024, verbose_name='Primary Package Mirror', blank=False)
    mirrorbasealt = models.URLField(max_length=1024, verbose_name='Alternate Package Mirror', blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @cached_property
    def dns_serialno(self):
        '''
        Locate the latest changed device, and use that date to derive the
        DNS Serial Number. The DNS Serial Number is formatted as:

        YYYYMMDDNN

        YYYY - Four digit year (zero padded)
        MM   - Two digit month (zero padded)
        DD   - Two digit day of month (zero padded)
        NN   - Two digit number of devices updated today (zero padded)
        '''

        # Calculate the beginning of today (UTC), so that we can figure out exactly
        # how many devices were updated today. This is part of the DNS serial number.
        today = make_aware(datetime.datetime.utcnow())
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        devices_updated_today = 0

        max_updated_at = self.updated_at
        for networkdevice in self.networkdevice_set.all():
            max_updated_at = max(max_updated_at, networkdevice.updated_at)
            if networkdevice.updated_at >= today:
                devices_updated_today += 1

        result = max_updated_at.strftime(r'%Y%m%d') + f'{devices_updated_today:02d}'
        return result

    @cached_property
    def drf_dnsrecords(self):
        '''Return all of the DNS records for all devices at this Site'''
        records = []

        # add external network records

        # DNS A Record is the forward lookup (primary hostname -> ipaddress)
        records.append({
            'hostname': f'borderexternal.{self.domain}',
            'record_type': 'A',
            'target': self.external_borderexternal,
        })

        # DNS A Record is the forward lookup (primary hostname -> ipaddress)
        records.append({
            'hostname': f'borderuplink.{self.domain}',
            'record_type': 'A',
            'target': self.external_borderuplink,
        })

        # DNS A Record is the forward lookup (primary hostname -> ipaddress)
        records.append({
            'hostname': f'border.{self.domain}',
            'record_type': 'A',
            'target': self.gateway,
        })

        # DNS CNAME is a name alias (alt-name -> name)
        records.append({
            'hostname': f'jadehost.{self.domain}',
            'record_type': 'CNAME',
            'target': f'pubsub.{self.domain}',
        })

        # DNS CNAME is a name alias (alt-name -> name)
        records.append({
            'hostname': f'jtcs.{self.domain}',
            'record_type': 'CNAME',
            'target': f'pubsub.{self.domain}',
        })

        # DNS CNAME is a name alias (alt-name -> name)
        records.append({
            'hostname': f'pubsubhost.{self.domain}',
            'record_type': 'CNAME',
            'target': f'pubsub.{self.domain}',
        })

        # DNS CNAME is a name alias (alt-name -> name)
        records.append({
            'hostname': f'dbhost.{self.domain}',
            'record_type': 'CNAME',
            'target': f'pubsubdb.{self.domain}',
        })

        for networkdevice in self.networkdevice_set.all():
            records.extend(networkdevice.drf_dnsrecords)

        return records

    @cached_property
    def drf_dhcprecords(self):
        '''Return all of the DHCP records for all devices at this Site'''
        records = []

        for networkdevice in self.networkdevice_set.all():
            records.extend(networkdevice.drf_dhcprecords)

        return records

    @cached_property
    def drf_unrecognized_devices(self):
        '''Return all UnrecognizedPXEDevice records at this Site'''
        result = []

        for device in UnrecognizedPXEDevice.objects.all():
            if device.site == self:
                result.append(device)

        return result

    @cached_property
    def drf_dashboard_data(self):
        '''Generate some data for a specific dashboard view'''
        # calculate cutoff (24h ago)
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=24)

        # calculate number of unrecognized devices since the cutoff
        unrecognized_device_count = 0
        for device in UnrecognizedPXEDevice.objects.filter(created_at__gte=cutoff).all():
            if device.site == self:
                unrecognized_device_count += 1

        # build queryset for all boot count information since the cutoff
        queryset = BootHistory.objects.filter(created_at__gte=cutoff)
        queryset = queryset.filter(puppetmachine__networkdevice__site__id=self.pk)

        return {
            'unrecognized_device_count': unrecognized_device_count,
            'boot_mode_local_count': queryset.filter(boot_mode='local').count(),
            'boot_mode_rebuild_count': queryset.filter(boot_mode='rebuild').count(),
            'boot_mode_rebuildalt_count': queryset.filter(boot_mode='rebuildalt').count(),
            'boot_mode_rescue_count': queryset.filter(boot_mode='rescue').count(),
        }

    @cached_property
    def netmask(self):
        return ip_network(f'{self.networkip}/{self.networkcidr}').netmask

    @cached_property
    def device_count(self):
        return self.networkdevice_set.count()

    def __unicode__(self):
        return f'Site(code="{self.code}")'

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ['code', ]

    def save(self, *args, **kwargs):
        # The adding flag indicates CREATE vs. UPDATE
        adding = self._state.adding
        operation = 'CREATE' if adding else 'UPDATE'
        print(f'Site::save: {operation}')
        return super().save(*args, **kwargs)

    def delete(self):
        print(f'Site::delete: DELETE')
        return super().delete()

class NTPServer(models.Model):
    # Link to parent Site object
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=False)
    # NTP Server Hostname / IP Address
    hostname = models.CharField(max_length=1024, verbose_name='NTP Server Hostname/IP Address', blank=False)
    # NTPd/Chronyd Configuration Options ("iburst prefer minpoll 4 maxpoll 4")
    options = models.CharField(max_length=1024, verbose_name='NTP Configuration Options', blank=True, default='')
    # For ordering in database queries
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return f'NTPServer(site={self.site.code}, hostname={self.hostname}, options={self.options})'

    class Meta:
        ordering = ['created_at', ]

class History(models.Model):
    '''Store the history of requests for easier troubleshooting'''

    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now_add=True)
    ipaddress = models.GenericIPAddressField(verbose_name='IP Address', protocol='ipv4')
    url = models.CharField(verbose_name='Request', max_length=64)
    success = models.BooleanField(verbose_name='Success', default=False)

    def __unicode__(self):
        return '%s %s %s %s' % (self.timestamp, self.ipaddress, self.url, self.success)

    class Meta:
        ordering = ['timestamp', ]

@receiver(post_save, sender=History)
def history_post_save(sender, **kwargs):
    # automatically remove any history items older than 7 days
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    cutoff = make_aware(cutoff)
    count = History.objects.filter(timestamp__lt=cutoff).delete()
    print(f'DELETE {count} History objects in prune operation')

class Machine(models.Model):
    SITE_CHOICES = (
        ( 'bpl', 'BPL - Santa Barbara Back Parking Lot', ),
        ( 'coj', 'COJ - Siding Spring, Australia', ),
        ( 'cpt', 'CPT - SAAO Sutherland, South Africa', ),
        ( 'elp', 'ELP - McDonald Observatory, Texas', ),
        ( 'lpl', 'LPL - Liverpool, England', ),
        ( 'lsc', 'LSC - Cerro Tololo, Chile', ),
        ( 'mfg', 'MFG - Manufacturing', ),
        ( 'ngq', 'NGQ - Tibet', ),
        ( 'ogg', 'OGG - Haleakala, Hawaii', ),
        ( 'ptr', 'PTR - Photon Ranch, California', ),
        ( 'sba', 'SBA - Santa Barbara, California', ),
        ( 'sci', 'SCI - Science Domain, Santa Barbara, California', ),
        ( 'sqa', 'SQA - Sedgwick Reserve, California', ),
        ( 'tlv', 'TLV - Tel Aviv, Israel', ),
        ( 'tfn', 'TFN - Tenerife', ),
        ( 'wer', 'WER - Wayne Rosing', ),
        ( 'wtf', 'WTF - Warehouse Test Facility', ),
    )

    OSTYPE_CHOICES = (
        ( 'centos', 'CentOS', ),
        ( 'proxmox', 'Proxmox VE', ),
    )

    ARCH_CHOICES = (
        ( 'i386', 'i386', ),
        ( 'x86_64', 'x86_64', ),
    )

    NETCONF_CHOICES = (
        ( 'dhcp', 'dhcp', ),
        ( 'static', 'static', ),
    )

    PARTITION_CHOICES = (
        ( 'auto', 'Automatic - CentOS will choose for you', ),
        ( 'docknode', 'Docker node standard partition scheme', ),
        ( 'lcogt', 'LCOGT - LCOGT default partition scheme', ),
        ( 'prompt', 'Prompt - You will be prompted', ),
        ( 'pubsubdb', 'PubsubDB - PubsubDB standard partition scheme', ),
        ( 'simple', 'Simple - All space in one large partition', ),
        ( 'simple-8swap', 'Simple + 8GB swap - All space in one large partition + 8GB swap', ),
        ( 'simple-8swap-20var', 'Simple + 8GB swap + 20GB /var - All space in one large partition + 8GB swap + 20GB /var', ),
        ( 'custom', 'Custom - Custom partition scheme (advanced!)', ),
    )

    BOOT_MODE_CHOICES = (
        ( 'local', 'Boot from local disk', ),
        ( 'rebuild', 'Rebuild at next boot', ),
        ( 'rebuildalt', 'Rebuild at next boot (use alternate package mirror)', ),
        ( 'rescue', 'Rescue at next boot', ),
    )

    mac         = models.CharField(max_length=17, verbose_name='MAC Address', unique=True)

    site        = models.CharField(max_length=3, verbose_name='LCOGT Site',
                                   choices=SITE_CHOICES, blank=False, default='sba')

    ostype      = models.CharField(max_length=32, verbose_name='Operating System Type',
                                   choices=OSTYPE_CHOICES, blank=False, default='centos')

    osversion   = models.CharField(max_length=8, verbose_name='Operating System Version',
                                   blank=False, default='7')

    arch        = models.CharField(max_length=6, verbose_name='Architecture',
                                   choices=ARCH_CHOICES, blank=False, default='x86_64')

    netconf     = models.CharField(max_length=6, verbose_name='Method',
                                   choices=NETCONF_CHOICES, blank=False, default='dhcp')

    netdev      = models.CharField(max_length=32, verbose_name='Device', default='eth0')

    hostname    = models.CharField(max_length=128, verbose_name='Hostname', unique=True)

    ipaddress   = models.GenericIPAddressField(verbose_name='IP Address', protocol='ipv4',
                                               null=True)

    partition   = models.CharField(max_length=128, verbose_name='Partition Scheme',
                                   choices=PARTITION_CHOICES, blank=False, default='auto')

    partition_custom = models.TextField(verbose_name='Custom Partitioning', default='')

    boot_mode   = models.CharField(max_length=16, verbose_name='Boot mode',
                                   choices=BOOT_MODE_CHOICES, blank=False, default='rebuild')

    def __unicode__(self):
        return self.mac

    def get(self, key):
        value = ''
        if hasattr(self, key):
            value = getattr(self, key)

        if value is None or value == '':
            return self.get_default(key)
        else:
            return value

    def get_default(self, key):
        site = self.site.lower()
        siteoctet = {
            'bpl': '7',
            'coj': '10',
            'cpt': '8',
            'elp': '9',
            'lsc': '5',
            'mfg': '6',
            'ngq': '13',
            'ogg': '0',
            'ptr': '15',
            'sqa': '12',
            'tlv': '11',
            'tfn': '14',
            'wtf': '17',
        }

        if key == 'mac':
            return self.mac.lower().replace('-', ':')
        elif key == 'site':
            return site
        elif key == 'ostype':
            return self.ostype
        elif key == 'osversion':
            return self.osversion
        elif key == 'arch':
            return self.arch
        elif key == 'netconf':
            return 'dhcp'
        elif key == 'netdev':
            return 'eth0'
        elif key == 'hostname':
            return ''
        elif key == 'ipaddress':
            return ''
        elif key == 'netmask':
            if site in ('sba', 'wer', ):
                return '255.255.252.0'
            elif site == 'sci':
                return '255.255.255.240'
            else:
                return '255.255.0.0'
        elif key == 'gateway':
            if site in ('sba', 'wer', ):
                return '172.16.5.253'
            elif site == 'sci':
                return '207.71.248.238'
            else:
                return '10.%s.0.254' % siteoctet[site]
        elif key == 'nameserver':
            if site in ('sba', 'wer', ):
                return '172.16.5.6,172.16.5.13'
            elif site == 'sci':
                return '172.16.5.6,172.16.5.13'
            else:
                return '172.16.5.6,10.%s.0.15,172.16.5.13' % siteoctet[site]
        elif key == 'partition':
            return 'prompt'
        elif key == 'boot_mode':
            return 'local'
        elif key == 'mirrorbasealt':
            # alternative mirror is always this fixed hostname
            return 'http://sba-bridge.%s.lco.gtn/repos' % site
        elif key == 'mirrorbase':
            # this machine is currently in "rebuild from alternate mirror" mode
            if self.boot_mode == 'rebuildalt':
                return self.get_default('mirrorbasealt')

            # core class machines will default to SBA mirror
            if re.match(r'^core\d.*\.lco.gtn$', self.hostname):
                return 'http://packagerepo.lco.gtn/repos'

            # these sites do not have a local package mirror
            if site not in ('bpl', 'mfg', 'sba', 'sci', 'wer', 'wtf', ):
                return 'http://core1.%s.lco.gtn/repos' % site

            # default
            return 'http://packagerepo.lco.gtn/repos'
        elif key == 'partition_custom':
            return '# None specified'
        else:
            raise Exception('Unknown variable key=%s passed to site_default() function' % key)

    class Meta:
        ordering = ['site', 'hostname', ]

    def save(self, *args, **kwargs):
        # The adding flag indicates CREATE vs. UPDATE
        adding = self._state.adding
        operation = 'CREATE' if adding else 'UPDATE'
        print(f'Machine::save: {operation}')
        return super().save(*args, **kwargs)

    def delete(self):
        print(f'Machine::delete: DELETE')
        return super().delete()

class NetworkDevice(models.Model):
    '''
    Database Model representing a Generic Network Device

    This class was designed after much thought to be able to represent
    any sort of physical device, as well as describing how to create all
    possible combinations of DHCP and DNS A/CNAME/PTR records.
    '''
    # Record Create / Update Time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Every device is at a site
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Telescope Site', blank=False)

    # Optional Image to describe the device
    image = models.ImageField(max_length=256, verbose_name='Device Image', blank=True, null=True)

    # Optional Freeform Text (HTML and Markdown formats are both supported).
    # This data is deemed to be safe (the user is assumed to be trusted and not to
    # intentionally break things). This is an LCO-internal tool.
    information = models.TextField(max_length=(128 * 1024), blank=True)

    # Optional FMX Documentation / Management URL
    fmxurl = models.URLField(max_length=4096, verbose_name='FMX URL', default='', blank=True)

    # Note implicit one-to-one field "puppetmachine"
    # Note implicit one-to-one field "webcam"

    # Convenience method (Python code only)
    def find_interface(self, macaddress):
        for netinterface in self.networkinterface_set.all():
            if netinterface.mac == macaddress:
                return netinterface

        return None

    # Convenience method (Python code only)
    @cached_property
    def primary_mac(self):
        '''Return first configured MAC address (Ethernet hardware address), or None'''
        for netinterface in self.networkinterface_set.all():
            return netinterface.mac

        return None

    # Convenience method (Python code only)
    @cached_property
    def primary_staticip(self):
        '''Return first configured static IP address (IPv4 address), or None'''
        for netinterface in self.networkinterface_set.all():
            for configuration in netinterface.networkinterfaceconfiguration_set.all():
                if configuration.ipaddress != '':
                    return configuration.ipaddress

        return None

    # Convenience method (Python code only)
    @cached_property
    def primary_hostname(self):
        '''Return first configured hostname, or None'''
        for netinterface in self.networkinterface_set.all():
            for configuration in netinterface.networkinterfaceconfiguration_set.all():
                for hostname in configuration.hostname_set.all():
                    if hostname.hostname != '':
                        return hostname.hostname

        return None

    @cached_property
    def drf_dnsrecords(self):
        records = []

        for netinterface in self.networkinterface_set.all():
            for configuration in netinterface.networkinterfaceconfiguration_set.all():
                hostname_set = list(configuration.hostname_set.all())
                primary_hostname = hostname_set[0]
                aliases = hostname_set[1:]

                if configuration.ipaddress is not None:
                    # DNS A Record is the forward lookup (primary hostname -> ipaddress)
                    records.append({
                        'hostname': primary_hostname.hostname,
                        'record_type': 'A',
                        'target': configuration.ipaddress,
                    })

                    # calculate the "in-addr.arpa" hostname for this IP Address
                    reverse_pointer = ip_address(configuration.ipaddress).reverse_pointer

                    # DNS PTR Record is the reverse lookup (ipaddress -> primary hostname)
                    records.append({
                        'hostname': reverse_pointer,
                        'record_type': 'PTR',
                        'target': primary_hostname.hostname,
                    })

                # DNS CNAME Record is an alias (alternative name) for the primary hostname
                for alias in aliases:
                    records.append({
                        'hostname': alias.hostname,
                        'record_type': 'CNAME',
                        'target': primary_hostname.hostname,
                    })

        # Return all DNS Records
        return records

    @cached_property
    def drf_dhcprecords(self):
        '''Calculate all DHCP records for this NetworkDevice'''
        records = []

        for netinterface in self.networkinterface_set.all():
            primary_configuration = netinterface.networkinterfaceconfiguration_set.first()
            primary_hostname = primary_configuration.hostname_set.first()

            # Skip devices which use DHCP
            if primary_configuration.ipaddress is None:
                continue

            records.append({
                'macaddress': netinterface.mac,
                'ipaddress': primary_configuration.ipaddress,
                'hostname': primary_hostname.hostname,
            })

        return records

    def save(self, *args, **kwargs):
        # The adding flag indicates CREATE vs. UPDATE
        adding = self._state.adding
        operation = 'CREATE' if adding else 'UPDATE'
        print(f'NetworkDevice::save: {operation}')
        return super().save(*args, **kwargs)

    def delete(self):
        print(f'NetworkDevice::delete: DELETE')
        return super().delete()

class NetworkInterface(models.Model):
    '''
    Database Model representing a Network Interface

    A Network Interface represents a single physical Ethernet interface.
    An Ethernet Interface has a Hardware Address (MAC Address) and zero
    or more IP Addresses.

    If <=0 IP Addresses: DHCP only
    If >=1 IP Addresses: DHCP + Static Config
    '''
    # Link to parent Network Device
    networkdevice = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE, blank=False)

    # Data Fields
    description = models.CharField(max_length=256, verbose_name='Description', blank=True)
    mac = models.CharField(max_length=17, verbose_name='MAC Address', unique=True)

    # Convenience method (Python code only)
    @cached_property
    def primary_staticip(self):
        '''Return first configured static IP address (IPv4 address), or None'''
        for configuration in self.networkinterfaceconfiguration_set.all():
            if configuration.ipaddress != '':
                return configuration.ipaddress

        return None

    # Convenience method (Python code only)
    @cached_property
    def primary_hostname(self):
        '''Return first configured hostname, or None'''
        for configuration in self.networkinterfaceconfiguration_set.all():
            for hostname in configuration.hostname_set.all():
                if hostname.hostname != '':
                    return hostname.hostname

        return None

    def save(self, *args, **kwargs):
        # The adding flag indicates CREATE vs. UPDATE
        adding = self._state.adding
        operation = 'CREATE' if adding else 'UPDATE'
        print(f'NetworkInterface::save: {operation}')
        return super().save(*args, **kwargs)

    def delete(self):
        print(f'NetworkInterface::delete: DELETE')
        return super().delete()

class NetworkInterfaceConfiguration(models.Model):
    '''
    Database Model representing an IP Address Configuration

    If both fields are filled in, this also represents a set of DNS A and DNS PTR
    records for this Network Device. Additionally, a DHCP record will be created
    to do "Static DHCP" (where DHCP is configured to hand out a specific IP to a
    specific MAC address).

    If the IP Address field is null, then this device is automatically configured
    via DHCP, and does not need an DNS A/PTR records created automatically.
    '''
    # Link to parent Network interface
    networkinterface = models.ForeignKey(NetworkInterface, on_delete=models.CASCADE, blank=False)

    # Data Fields
    ipaddress = models.GenericIPAddressField(verbose_name='IP Address', protocol='ipv4', blank=True, null=True)
    # NOTE: implicit list of Hostname objects available in the "hostname_set" member

    def __unicode__(self):
        return f'NetworkInterfaceConfiguration(ip={self.ipaddress}, hostname={self.hostname}, aliases={",".join(self.aliases)})'

    def save(self, *args, **kwargs):
        # The adding flag indicates CREATE vs. UPDATE
        adding = self._state.adding
        operation = 'CREATE' if adding else 'UPDATE'
        print(f'NetworkInterfaceConfiguration::save: {operation}')
        return super().save(*args, **kwargs)

    def delete(self):
        print(f'NetworkInterfaceConfiguration::delete: DELETE')
        return super().delete()

class Hostname(models.Model):
    # Link to parent NetworkInterfaceConfiguration object
    networkinterfaceconfiguration = models.ForeignKey(NetworkInterfaceConfiguration, on_delete=models.CASCADE, blank=False)
    # Unique hostname
    hostname = models.CharField(max_length=256, verbose_name='Hostname', unique=True)
    # For ordering in database queries
    created_at = models.DateTimeField(auto_now_add=True)

class Webcam(models.Model):
    # Associated NetworkDevice
    # Note that the primary key of the NetworkDevice and corresponding
    # Webcam are *always* exactly the same!
    networkdevice = models.OneToOneField(
        NetworkDevice,
        on_delete=models.CASCADE,
        verbose_name='Network Device',
        primary_key=True,
    )

    adminurl = models.URLField(max_length=1024, verbose_name='Webcam Administration Interface URL', blank=False)
    imageurl = models.URLField(max_length=1024, verbose_name='Webcam Image Fetch URL', blank=False)
    is_enabled = models.BooleanField(verbose_name='Is this Webcam enabled?', default=True)
    is_public = models.BooleanField(verbose_name='Is this Webcam available to the Public Internet?', default=False)
    is_dome = models.BooleanField(verbose_name='Is this Webcam a Dome Camera?', default=False)

    def save(self, *args, **kwargs):
        # The adding flag indicates CREATE vs. UPDATE
        adding = self._state.adding
        operation = 'CREATE' if adding else 'UPDATE'
        print(f'Webcam::save: {operation}')
        return super().save(*args, **kwargs)

    def delete(self):
        print(f'Webcam::delete: DELETE')
        return super().delete()

class PuppetMachine(models.Model):
    # Associated NetworkDevice
    # Note that the primary key of the NetworkDevice and corresponding
    # PuppetMachine are *always* exactly the same!
    networkdevice = models.OneToOneField(
        NetworkDevice,
        on_delete=models.CASCADE,
        verbose_name='Network Device',
        primary_key=True,
    )

    OPERATINGSYSTEM_CHOICES = (
        ('centos-5-i386', 'CentOS 5 i386'),
        ('centos-5-x86_64', 'CentOS 5 x86_64'),
        # NOTE: The CentOS 6 i686 arch is really i386 within the operating system and
        # RPM packaging ecosystem. But in reality, only i686 hardware is supported.
        # The CentOS 6 OS requires a CPU with the Intel x86 PAE extensions (and also
        # possibly MMX and SSE) in order to boot. That's why we designate it "i686"
        # in the UI.
        ('centos-6-i386', 'CentOS 6 i686'),
        ('centos-6-x86_64', 'CentOS 6 x86_64'),
        ('centos-7-x86_64', 'CentOS 7 x86_64'),
        ('centos-8-x86_64', 'CentOS 8 x86_64'),
        ('proxmox-61-x86_64', 'Proxmox VE 6.1 x86_64'),
    )
    operatingsystem = models.CharField(max_length=256, verbose_name='Operating System',
                                       choices=OPERATINGSYSTEM_CHOICES, blank=False,
                                       default='centos-7-x86_64')

    # Disk Partition Scheme
    PARTITIONSCHEME_CHOICES = (
        ( 'auto', 'Automatic - CentOS will choose for you', ),
        ( 'docknode', 'Docker node standard partition scheme', ),
        ( 'lcogt', 'LCOGT - LCOGT default partition scheme', ),
        ( 'prompt', 'Prompt - You will be prompted', ),
        ( 'pubsubdb', 'PubsubDB - PubsubDB standard partition scheme', ),
        ( 'simple', 'Simple - All space in one large partition', ),
        ( 'simple-8swap', 'Simple + 8GB swap - All space in one large partition + 8GB swap', ),
        ( 'simple-8swap-20var', 'Simple + 8GB swap + 20GB /var - All space in one large partition + 8GB swap + 20GB /var', ),
        ( 'custom', 'Custom - Custom partition scheme (advanced!)', ),
    )
    partitionscheme = models.CharField(max_length=32, verbose_name='Partition Scheme', blank=False,
                                       choices=PARTITIONSCHEME_CHOICES, default='simple')
    partitionscheme_custom = models.TextField(verbose_name='Custom Partition Scheme', blank=True)

    # Boot Mode
    BOOT_MODE_CHOICES = (
        ( 'local', 'Boot from local disk', ),
        ( 'rebuild', 'Rebuild at next boot', ),
        ( 'rebuildalt', 'Rebuild at next boot (use alternate package mirror)', ),
        ( 'rescue', 'Rescue at next boot', ),
    )
    boot_mode = models.CharField(max_length=32, verbose_name='Boot Mode', blank=False,
                                 choices=BOOT_MODE_CHOICES, default='local')

    def save(self, *args, **kwargs):
        # The adding flag indicates CREATE vs. UPDATE
        adding = self._state.adding
        operation = 'CREATE' if adding else 'UPDATE'
        print(f'PuppetMachine::save: {operation}')
        return super().save(*args, **kwargs)

    def delete(self):
        print(f'PuppetMachine::delete: DELETE')
        return super().delete()

    @cached_property
    def ostype(self):
        return self.operatingsystem.split('-')[0]

    @cached_property
    def osversion(self):
        return self.operatingsystem.split('-')[1]

    @cached_property
    def arch(self):
        return self.operatingsystem.split('-')[2]

    @property
    def lastboot_at(self):
        '''The timestamp of the latest boot'''
        elem = self.boothistory_set.order_by('-created_at').first()
        if elem is not None:
            return elem.created_at

        return None

    @property
    def boot_history(self):
        return self.boothistory_set.order_by('-created_at').all()

    @property
    def lastbuild_at(self):
        '''The timestamp of the latest build'''
        elem = self.buildhistory_set.order_by('-created_at').first()
        if elem is not None:
            return elem.created_at

        return None

    @property
    def build_history(self):
        return self.buildhistory_set.order_by('-created_at').all()

    @property
    def mirrorbase(self):
        site = self.networkdevice.site
        boot_mode = self.boot_mode
        mirrorbase = site.mirrorbasealt if boot_mode.endswith('alt') else site.mirrorbase
        return mirrorbase

    @cached_property
    def facts(self):
        '''Fetch and return PuppetDB Facter Facts'''
        hostname = self.networkdevice.primary_hostname
        if hostname is None:
            return None

        # Fetch Puppet Facts from PuppetDB
        facts = puppetdb_facts(hostname)
        return [{'name': elem['name'], 'value': elem['value'], } for elem in facts]

    @cached_property
    def lcogtinstruments(self):
        '''PuppetDB $::lcogtinstruments fact direct access (convenience shortcut for API users)'''
        facts = self.facts
        for elem in facts:
            if elem.get('name', None) == 'lcogtinstruments':
                return elem.get('value', None)

        return None

    def get_fact_value(self, fact_name):
        '''Get the value of a Facter fact from PuppetDB (or return None if not found)'''
        if self.facts is not None:
            for elem in self.facts:
                if elem['name'] == fact_name:
                    return elem['value']

        return None

class BootHistory(models.Model):
    puppetmachine = models.ForeignKey(PuppetMachine, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    boot_mode = models.CharField(max_length=32, verbose_name='Boot Mode', blank=False,
                                 choices=PuppetMachine.BOOT_MODE_CHOICES, default='local')

class BuildHistory(models.Model):
    puppetmachine = models.ForeignKey(PuppetMachine, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, verbose_name='Status', blank=True)

class UnrecognizedPXEDevice(models.Model):
    '''
    An Unrecognized PXE Device booted up, we need to keep a record of this so
    that we can onboard it into the system semi-automatically for the user.
    '''
    mac = models.CharField(max_length=17, verbose_name='MAC Address')
    ipaddress = models.GenericIPAddressField(verbose_name='IP Address', protocol='ipv4')
    data = models.TextField(max_length=(128 * 1024), verbose_name='Data', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @cached_property
    def site(self):
        ipaddress = ip_address(self.ipaddress)
        for site in Site.objects.all():
            if ipaddress in ip_network(f'{site.networkip}/{site.networkcidr}'):
                return site

        return None

    @cached_property
    def found(self):
        return NetworkInterface.objects.filter(mac__iexact=self.mac).count() > 0

    @cached_property
    def networkdevice_id(self):
        netinterface = NetworkInterface.objects.filter(mac__iexact=self.mac).first()
        if netinterface is None:
            return None

        return netinterface.networkdevice.id

# vim: set ts=4 sts=4 sw=4 et tw=112:
