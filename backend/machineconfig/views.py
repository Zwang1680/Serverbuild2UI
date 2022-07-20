#!/usr/bin/env python

from urllib.parse import unquote

import base64
import crypt
import os

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from machineconfig.models import BootHistory
from machineconfig.models import BuildHistory
from machineconfig.models import PuppetMachine
from machineconfig.models import NetworkDevice
from machineconfig.models import UnrecognizedPXEDevice

################################################################################
# Generic Helper Methods
################################################################################

def request_client_ipaddress(request):
    '''Retrieve the client IP address, either directly or from the proxy headers'''
    ipaddress = request.META.get('REMOTE_ADDR')
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ipaddress = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0].strip()

    return ipaddress

def request_is_internal(request):
    '''
    Return True if the request is internal (made by the web client).
    False otherwise (usually a real PXE ROM client).
    '''
    return request.GET.get('internal', None) is not None

################################################################################
# TFTP Helper Methods
################################################################################

def tftp_network_configuration(networkdevice, macaddress):
    '''
    Generate the TFTP network configuration string for a given machine,
    taking all of the differences between CentOS versions into account.
    '''
    # Helper variables for shorter code
    puppetmachine = networkdevice.puppetmachine
    site = networkdevice.site

    # This function can only handle CentOS machines
    assert puppetmachine.ostype == 'centos'
    osversion = int(puppetmachine.osversion)

    ipaddress = networkdevice.primary_staticip
    is_dhcp = (ipaddress == None)

    elements = []

    # CentOS 5 must specify the exact network device to boot from
    # CentOS 6+ understands that it should use the boot interface MAC address
    if osversion <= 5:
        elements.append('ksdevice=eth0')
    else:
        elements.append('ksdevice=bootif')

    # CentOS 5 cannot do TFTP with a static address configuration due to severe
    # command line length restrictions. Newer versions work fine. The kickstart
    # file will set up the correct network device and address configuration.
    if is_dhcp or osversion <= 5:
        elements.append('ip=dhcp')
        return ' '.join(elements)

    # CentOS 6 knows how to understand comma-separated DNS servers
    if osversion == 6:
        elements.append(f'ip={ipaddress}')
        elements.append(f'netmask={site.netmask}')
        elements.append(f'gateway={site.gateway}')
        elements.append(f'dns={",".join(site.dnsservers)}')
        return ' '.join(elements)

    # CentOS 7 deprecated the various separated options, and instead uses a
    # unified "ip=" syntax. It also cannot understand comma-separated DNS
    # servers: you must specify them individually.
    #
    # It also has the ability to pick the name for each network interface,
    # which is specified by MAC address. This makes the setup a bit easier,
    # since we don't need to guess the unpredictable network device name
    # anymore. To make things easy, we always call our boot interface 'eth0'.
    #
    # CentOS 8 is compatible with CentOS 7 in this case.
    if osversion == 7 or osversion == 8:
        hostname = networkdevice.primary_hostname
        elements.append(f'ifname=eth0:{macaddress}')
        elements.append(f'ip={ipaddress}::{site.gateway}:{site.netmask}:{hostname}:eth0:none')
        for nameserver in site.dnsservers:
            elements.append(f'nameserver={nameserver}')

        return ' '.join(elements)

    # Unsupported CentOS version detected
    raise RuntimeError('Unknown CentOS Major Version: %d' % osversion)

def tftp_extra(networkdevice):
    '''
    Generate extra TFTP paramaters for a given PuppetMachine.
    '''
    # Helper variables for shorter code
    puppetmachine = networkdevice.puppetmachine

    # This function can only handle CentOS machines
    assert puppetmachine.ostype == 'centos'

    extra = []
    osversion = int(puppetmachine.osversion)

    # Enable users to monitor Anaconda installer over SSH
    if osversion == 6:
        extra.append('sshd=1')
    elif osversion >= 7:
        extra.append('sshd')

    # This is very old hardware, and the graphics hardware is so poor
    # that it cannot work in graphical mode at all on newer OS versions
    if networkdevice.primary_hostname.startswith('fs.') and osversion >= 7:
        extra.append('inst.text')

    return ' '.join(extra)

def save_unrecognized_device_record(request):
    '''
    Create a new UnrecognizedPXEDevice record in the database (if possible)
    '''

    # PXELinux sends a bunch of information in the COOKIES header
    # Here is a complete example taken from a real request (KVM virtual machine):
    # _Syslinux_ip=172.16.4.46%3A172.16.5.1%3A172.16.5.253%3A255.255.252.0
    # _Syslinux_BOOTIF=01-52-54-00-e3-cc-00
    # _Syslinux_SYSUUID=85c4846a-f5fc-144c-9c65-9684cdd8f815
    # _Syslinux_CPU=6PXL
    # _Syslinux_SYSVENDOR=Red+Hat
    # _Syslinux_SYSPRODUCT=KVM
    # _Syslinux_SYSVERSION=RHEL+7.0.0+PC+%28i440FX+++PIIX%2C+1996%29
    # _Syslinux_SYSFAMILY=Red+Hat+Enterprise+Linux
    # _Syslinux_BIOSVENDOR=Seabios
    # _Syslinux_BIOSVERSION=0.5.1
    # _Syslinux_SYSFF=1

    # Data: all syslinux cookies
    data = []
    for (k, v) in request.COOKIES.items():
        if k.startswith('_Syslinux_'):
            data.append(f'{k}={v}')

    # Nothing sent, must not be PXELinux. We can't convert this into a NetworkDevice
    # semi-automatically to help out our user. Sorry.
    if len(data) <= 0:
        print('No "_Syslinux_" cookies found... not a real device? Test request?')
        return

    # Convert to a text field
    data = '\n'.join(data)

    # MAC Address (Ethernet hardware address)
    macaddress = request.COOKIES.get('_Syslinux_BOOTIF', '')
    macaddress = ':'.join(macaddress.split('-')[1:])
    macaddress = macaddress.lower()

    # IP Address (IPv4 Address)
    ipaddress = request.COOKIES.get('_Syslinux_ip', '')
    ipaddress = unquote(ipaddress)
    ipaddress = ipaddress.split(':')
    ipaddress = ipaddress[0]

    # Create the UnrecognizedPXEDevice database record
    device = UnrecognizedPXEDevice.objects.create(
        mac=macaddress,
        ipaddress=ipaddress,
        data=data,
    )

    return device

################################################################################
# Kickstart Helper Methods
################################################################################

def kickstart_netconf(networkdevice, macaddress):
    '''Is this device DHCP or Static IP configuration?'''
    netinterface = networkdevice.find_interface(macaddress)
    if netinterface is not None:
        ipaddress = netinterface.primary_staticip
        if ipaddress is not None:
            return 'static'

    return 'dhcp'

def kickstart_hostname(networkdevice, macaddress):
    netinterface = networkdevice.find_interface(macaddress)
    if netinterface is not None:
        hostname = netinterface.primary_hostname
        if hostname is not None:
            return hostname

    return ''

def kickstart_crypt_password(puppetmachine, password):
    '''Generate the encrypted root password with a random salt'''
    # This function can only handle CentOS machines
    assert puppetmachine.ostype == 'centos'

    # constants
    CRYPT_METHOD_MD5 = '1'
    CRYPT_METHOD_SHA512 = '6'

    # default to sha512
    crypt_method = CRYPT_METHOD_SHA512

    # CentOS 5 can only handle MD5 passwords
    if int(puppetmachine.osversion) <= 5:
        crypt_method = CRYPT_METHOD_MD5

    # generate a random salt each time this function is used
    crypt_salt_base64 = base64.b64encode(os.urandom(32)).decode('utf-8')
    crypt_salt = '$%s$%s$' % (crypt_method, crypt_salt_base64)

    # crypt the password with the random salt
    return crypt.crypt(password, crypt_salt)

def kickstart_network_configuration(networkdevice, macaddress):
    '''
    Generate the Anaconda Kickstart network configuration string for a given machine,
    taking all of the differences between CentOS versions into account.
    '''
    # Helper variables for shorter code
    puppetmachine = networkdevice.puppetmachine
    site = networkdevice.site

    # This function can only handle CentOS machines
    assert puppetmachine.ostype == 'centos'

    netconf = kickstart_netconf(networkdevice, macaddress)
    osversion = int(puppetmachine.osversion)
    elements = []

    elements.append(f'network')
    elements.append(f'--bootproto={netconf}')

    # CentOS 5 requires a device name (almost always eth0)
    # CentOS 6 and later can use the MAC address (another alternative
    # is to use --device=bootif and rely on PXELinux, but we'll be explicit)
    if osversion <= 5:
        elements.append(f'--device=eth0')
    else:
        elements.append(f'--device={macaddress}')

    elements.append(f'--hostname={kickstart_hostname(networkdevice, macaddress)}')

    # if this is a DHCP configuration, we're done
    if netconf == 'dhcp':
        return ' '.join(elements)

    # Static IPv4 Configuration
    ipaddress = networkdevice.primary_staticip
    elements.append(f'--ip={ipaddress}')
    elements.append(f'--netmask={site.netmask}')
    elements.append(f'--gateway={site.gateway}')

    # No DNS Servers, we're done
    if len(site.dnsservers) <= 0:
        return ' '.join(elements)

    # CentOS 5 can only handle a single nameserver
    if osversion == 5:
        elements.append(f'--nameserver={site.dnsservers[0]}')

    # CentOS 6 can handle multiple nameservers (comma separated)
    if osversion == 6:
        elements.append(f'--nameserver={",".join(site.dnsservers)}')

    # CentOS 7 requires multiple nameserver arguments
    # CentOS 8 is compatible with CentOS 7 in this case.
    if osversion == 7 or osversion == 8:
        for nameserver in site.dnsservers:
            elements.append(f'--nameserver={nameserver}')

    # Join everything together, we're done
    return ' '.join(elements)

def kickstart_fstype_bootable(puppetmachine):
    '''
    Retrieve the fstype for /boot partitions based on the CentOS version.
    This partition type is bootable by GRUB on this CentOS version.
    '''
    # This function can only handle CentOS machines
    assert puppetmachine.ostype == 'centos'

    osversion = int(puppetmachine.osversion)
    if osversion == 5:
        return 'ext3'
    elif osversion == 6:
        return 'ext4'
    elif osversion == 7:
        return 'xfs'
    elif osversion == 8:
        return 'xfs'

    raise RuntimeError('Unknown CentOS Major Version: %d' % osversion)

def kickstart_fstype_root(puppetmachine):
    '''
    Retrieve the fstype for / partitions based on the CentOS version.
    This partition type is bootable by the initrd on this CentOS version.
    '''
    # This function can only handle CentOS machines
    assert puppetmachine.ostype == 'centos'

    osversion = int(puppetmachine.osversion)
    if osversion == 5:
        return 'ext3'
    elif osversion == 6:
        return 'ext4'
    elif osversion == 7:
        return 'xfs'
    elif osversion == 8:
        return 'xfs'

    raise RuntimeError('Unknown CentOS Major Version: %d' % osversion)

def kickstart_fstype_other(puppetmachine):
    '''
    Retrieve the fstype for all other partitions based on the CentOS version.
    This partition type is accessible by this CentOS version after initrd is
    finished and we are running the full userspace.
    '''
    # This function can only handle CentOS machines
    assert puppetmachine.ostype == 'centos'

    osversion = int(puppetmachine.osversion)
    if osversion == 5:
        return 'ext3'
    elif osversion == 6:
        return 'xfs'
    elif osversion == 7:
        return 'xfs'
    elif osversion == 8:
        return 'xfs'

    raise RuntimeError('Unknown CentOS Major Version: %d' % osversion)

def stringify_pveversion(puppetmachine):
    '''
    Convert the Proxmox VE version into a prettier string version for display
    in the Web User Interface.

    For example, turns osversion='61' into '6.1'.
    '''
    # This function can only handle Proxmox VE machines
    assert puppetmachine.ostype == 'proxmox'

    osversion = puppetmachine.osversion
    return '{}.{}'.format(osversion[0], osversion[1:])

################################################################################
# Django Views
################################################################################

@require_http_methods(['GET'])
def tftp_default(request):
    '''View to render the PXELinux TFTP default configuration file'''

    # Save "unrecognized PXE device" record for later "promotion" to a
    # full NetworkDevice in the web interface
    save_unrecognized_device_record(request)

    # MAC (possibly missing)
    macaddress = 'not-sent-by-pxelinux'
    cookie = request.COOKIES.get('_Syslinux_BOOTIF', None)
    if cookie is not None:
        macaddress = ':'.join(cookie.split('-')[1:])
        macaddress = macaddress.lower()

    # Jinja2 template parameters
    d = {
        'mac': macaddress,
        'tftpurl': request.build_absolute_uri('/tftp/' + macaddress),
        'baseurl': request.build_absolute_uri('/'),
    }

    return render(request, 'tftpdefault.jinja', d, content_type='text/plain')

@require_http_methods(['GET'])
def tftp(request, macaddress):
    '''View to render the PXELinux TFTP configuration file'''
    macaddress = macaddress.replace('-', ':')
    networkdevice = get_object_or_404(NetworkDevice, networkinterface__mac__iexact=macaddress)
    puppetmachine = networkdevice.puppetmachine
    site = networkdevice.site

    # History API: save "machine booted" record
    if not request_is_internal(request):
        BootHistory.objects.create(puppetmachine=puppetmachine, boot_mode=puppetmachine.boot_mode)

    # CentOS
    if puppetmachine.ostype == 'centos':
        d = {
            'site': site,
            'osversion': int(puppetmachine.osversion),
            'arch': puppetmachine.arch,
            'hostname': networkdevice.primary_hostname,
            'mirrorbase': puppetmachine.mirrorbase,
            'network_configuration': tftp_network_configuration(networkdevice, macaddress),
            'extra': tftp_extra(networkdevice),
            'tftpurl': request.build_absolute_uri('/tftp/' + macaddress),
            'ksurl': request.build_absolute_uri('/ks/' + macaddress),
            'boot_mode': puppetmachine.boot_mode,
        }
        template = f'{puppetmachine.ostype}/tftp.jinja'
        return render(request, template, d, content_type='text/plain')

    # Proxmox VE
    if puppetmachine.ostype == 'proxmox':
        d = {
            'site': site,
            'arch': puppetmachine.arch,
            'hostname': networkdevice.primary_hostname,
            'mirrorbase': puppetmachine.mirrorbase,
            'tftpurl': request.build_absolute_uri('/tftp/' + macaddress),
            'ksurl': request.build_absolute_uri('/ks/' + macaddress),
            'boot_mode': puppetmachine.boot_mode,
            'pveversion': stringify_pveversion(puppetmachine),
        }
        template = f'{puppetmachine.ostype}/tftp.jinja'
        return render(request, template, d, content_type='text/plain')

    # Unknown Operating System Type
    raise RuntimeError('Unknown Operating System Type: {}'.format(puppetmachine.ostype))

@require_http_methods(['GET'])
def kickstart(request, macaddress):
    '''View to render the Anaconda Kickstart configuration file'''
    macaddress = macaddress.replace('-', ':')
    networkdevice = get_object_or_404(NetworkDevice, networkinterface__mac__iexact=macaddress)
    puppetmachine = networkdevice.puppetmachine
    site = networkdevice.site

    # History API: save "build begin" record
    if not request_is_internal(request):
        if puppetmachine.boot_mode.startswith('rebuild'):
            BuildHistory.objects.create(
                puppetmachine=puppetmachine,
                status='BEGIN',
            )

    # CentOS
    if puppetmachine.ostype == 'centos':
        # passwords
        password_root = f'{site.code}cana1'
        crypt_password_root = kickstart_crypt_password(puppetmachine, password_root)

        password_eng = f'{site.code}too1'
        crypt_password_eng = kickstart_crypt_password(puppetmachine, password_eng)

        d = {
            'site': site,
            'osversion': int(puppetmachine.osversion),
            'arch': puppetmachine.arch,
            'hostname': networkdevice.primary_hostname,
            'partition': puppetmachine.partitionscheme,
            'partition_custom': puppetmachine.partitionscheme_custom,
            'mirrorbase': puppetmachine.mirrorbase,
            'crypt_password_root': crypt_password_root,
            'crypt_password_eng': crypt_password_eng,
            'network_configuration': kickstart_network_configuration(networkdevice, macaddress),
            'bootmodeurl': request.build_absolute_uri(f'/api/networkdevice/{networkdevice.pk}/bootmode/'),
            'boot_mode': puppetmachine.boot_mode,
            'fstype_bootable': kickstart_fstype_bootable(puppetmachine),
            'fstype_root': kickstart_fstype_root(puppetmachine),
            'fstype_other': kickstart_fstype_other(puppetmachine),
        }
        template = f'{puppetmachine.ostype}/kickstart.jinja'
        return render(request, template, d, content_type='text/plain')

    # Proxmox VE
    if puppetmachine.ostype == 'proxmox':
        # TODO FIXME
        d = {
            'site': site,
            'arch': puppetmachine.arch,
            'mirrorbase': puppetmachine.mirrorbase,
            'boot_mode': puppetmachine.boot_mode,
            'pveversion': stringify_pveversion(puppetmachine),
        }
        template = f'{puppetmachine.ostype}/kickstart.jinja'
        return render(request, template, d, content_type='text/plain')

    # Unknown Operating System Type
    raise RuntimeError('Unknown Operating System Type: {}'.format(puppetmachine.ostype))

# vim: set ts=4 sts=4 sw=4 et tw=112:
