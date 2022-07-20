#!/usr/bin/env python3

from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status

from rest_flex_fields import FlexFieldsModelViewSet
from django_filters import rest_framework as filters

from machineconfig.views import request_is_internal

from machineconfig.models import Site
from machineconfig.models import NetworkDevice
from machineconfig.models import PuppetMachine
from machineconfig.models import UnrecognizedPXEDevice
from machineconfig.models import BootHistory
from machineconfig.models import BuildHistory

from machineconfig.serializers import SiteSerializer
from machineconfig.serializers import NetworkDeviceSerializer
from machineconfig.serializers import UnrecognizedPXEDeviceSerializer
from machineconfig.serializers import BootHistorySerializer
from machineconfig.serializers import BuildHistorySerializer

import django_rq

from contextlib import ContextDecorator
import subprocess
import ipaddress
import datetime
import socket

class mycontext(ContextDecorator):
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        print('ENTER:', self.message)
        return self

    def __exit__(self, *exc):
        print('EXIT:', self.message)
        return False

def clamp(n, lower_bound, upper_bound):
    return max(lower_bound, min(n, upper_bound))

def make_simple_error(message):
    data = {
        'error': message,
    }
    return data

def run_ipmitool(networkdevice, command, timeout=15):
    '''
    Run the /usr/bin/ipmitool utility, with the given command. Return a Django
    REST Framework Response object. Example:

    run_ipmitool_command(networkdevice, command=['chassis', 'status'])
    '''
    puppetmachine = networkdevice.puppetmachine
    site = networkdevice.site

    username = 'ADMIN'
    password = f'{site.code.lower()}cana1'
    hostname = puppetmachine.get_fact_value('ipmi_ipaddress')

    if hostname is None:
        data = make_simple_error(f'No Puppet Fact ipmi_ipaddress available for NetworkDevice pk={networkdevice.pk}')
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    cmd = [
        '/usr/bin/ipmitool',
        '-U',
        str(username),
        '-P',
        str(password),
        '-H',
        str(hostname),
    ] + command

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    data = {
        #'command': cmd,
        'stdout': proc.stdout,
        'returncode': proc.returncode,
    }
    return Response(data, status=status.HTTP_200_OK)

def format_columnar_data(data):
    output = []
    widths = [max(map(len, col)) for col in zip(*data)]
    for row in data:
        output.append([val.ljust(width) for val, width in zip(row, widths)])

    return output

def run_puppet_agent_test(networkdevice_id, timeout=3600):
    print(f'run_puppet_agent_test: networkdevice_id={networkdevice_id}')
    networkdevice = NetworkDevice.objects.get(pk=networkdevice_id)
    puppet_command = '/usr/bin/sudo /opt/puppetlabs/bin/puppet agent --test'
    env = {
        'LANG': 'C',
        'LC_ALL': 'C',
    }
    cmd = [
        '/usr/bin/ssh',
        '-x',
        '-4',
        '-o',
        'StrictHostKeyChecking=no',
        '-t',
        '-t',
        '-i',
        '/app/ssh/id_rsa',
        f'eng@{networkdevice.primary_hostname}',
        puppet_command,
    ]
    proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    data = {
        'command': puppet_command,
        'stdout': proc.stdout,
        'returncode': proc.returncode,
    }
    return data

# ViewSets define the view behavior.
class SiteViewSet(FlexFieldsModelViewSet):
    queryset = Site.objects.all()
    queryset = queryset.prefetch_related('ntpserver_set')
    queryset = queryset.prefetch_related('networkdevice_set')
    queryset = queryset.prefetch_related('networkdevice_set__puppetmachine')
    queryset = queryset.prefetch_related('networkdevice_set__networkinterface_set')
    queryset = queryset.prefetch_related('networkdevice_set__networkinterface_set__networkinterfaceconfiguration_set')
    queryset = queryset.prefetch_related('networkdevice_set__networkinterface_set__networkinterfaceconfiguration_set__hostname_set')
    serializer_class = SiteSerializer
    permit_list_expands = [
        'devices',
        'dnsrecords',
        'dhcprecords',
        'unrecognized_devices',
        'dashboard_data',
    ]

    # This is the main entrypoint into the API once we have valid data.
    # Wrap this operation in an atomic database transaction, so that any
    # failures in database operations (CREATE/UPDATE) on nested objects will
    # fail the entire API operation, without leaving any orphaned sub-objects
    # in the database.
    @transaction.atomic
    @mycontext('SiteViewSet::perform_create')
    def perform_create(self, serializer):
        print(f'SiteViewSet::perform_create: CREATE')
        return super().perform_create(serializer=serializer)

    # This is the main entrypoint into the API once we have valid data.
    # Wrap this operation in an atomic database transaction, so that any
    # failures in database operations (CREATE/UPDATE) on nested objects will
    # fail the entire API operation, without leaving any orphaned sub-objects
    # in the database.
    @transaction.atomic
    @mycontext('SiteViewSet::perform_update')
    def perform_update(self, serializer):
        print(f'SiteViewSet::perform_update: UPDATE')
        return super().perform_update(serializer=serializer)

    # This is the main entrypoint into the API once we have valid data.
    # Wrap this operation in an atomic database transaction, so that any
    # failures in database operations (CREATE/UPDATE) on nested objects will
    # fail the entire API operation, without leaving any orphaned sub-objects
    # in the database.
    @transaction.atomic
    @mycontext('SiteViewSet::perform_destroy')
    def perform_destroy(self, instance):
        print(f'SiteViewSet::perform_destroy: DELETE')
        return super().perform_destroy(instance=instance)

    @action(detail=True, methods=['get', ])
    def dhcpconf(self, request, pk=None):
        site = self.get_object()
        sitenetwork = ipaddress.ip_network(f'{site.networkip}/{site.networkcidr}')
        dhcprange = None
        if str(sitenetwork.network_address).startswith('10.'):
            parts = str(sitenetwork.network_address).split('.')
            dhcprange = {
                'start': f'{parts[0]}.{parts[1]}.249.1',
                'end': f'{parts[0]}.{parts[1]}.249.99',
            }

        d = {
            'site': site,
            'sitenetwork': sitenetwork,
            'dhcprecords': site.drf_dhcprecords,
            'dhcprange': dhcprange,
        }
        return render(request, 'dhcpconf.jinja', d, content_type='text/plain')

    @action(detail=True, methods=['get', ], url_path='dnsconf/forward')
    def dnsconf_forward(self, request, pk=None):
        '''DNS Configuration in BIND "forward" format'''
        site = self.get_object()

        # Munge DNS records to get them into the format we need for the
        # template, so that we get ultra-pretty output, all the time
        dnsrecords = []

        # DNS NS records are automatically generated, but do need some dots added
        dnsrecords.append([
            f'{site.domain}.',
            'NS',
            f'core1.{site.domain}.',
        ])

        for record in site.drf_dnsrecords:
            record_type = record['record_type']
            hostname = record['hostname']
            target = record['target']

            # DNS A records need a dot added to the hostname only
            if record_type == 'A' and target is not None:
                dnsrecords.append([
                    f'{hostname}.',
                    record_type,
                    target,
                ])

            # DNS CNAME records need a dot addet to the hostname and target
            if record_type == 'CNAME' and target is not None:
                dnsrecords.append([
                    f'{hostname}.',
                    record_type,
                    f'{target}.',
                ])

        # Now format the whole thing into columnar data
        dnsrecords = format_columnar_data(dnsrecords)
        d = {
            'site': site,
            'dnsrecords': dnsrecords,
        }
        return render(request, 'dnsconf_forward.jinja', d, content_type='text/plain')

    @action(detail=True, methods=['get', ], url_path='dnsconf/reverse')
    def dnsconf_reverse(self, request, pk=None):
        '''DNS Configuration in BIND "reverse" format'''
        site = self.get_object()
        dnsrecords = [record for record in site.drf_dnsrecords if record['record_type'] in ('PTR', )]
        d = {
            'site': site,
            'dnsrecords': dnsrecords,
        }

        # Munge DNS records to get them into the format we need for the
        # template, so that we get ultra-pretty output, all the time
        dnsrecords = []

        # DNS NS records are automatically generated, but do need some dots added
        dnsrecords.append([
            f'{site.domain}.',
            'NS',
            f'core1.{site.domain}.',
        ])

        for record in site.drf_dnsrecords:
            record_type = record['record_type']
            hostname = record['hostname']
            target = record['target']

            # DNS PTR records need a dot added to both the hostname and target
            if record_type == 'PTR':
                dnsrecords.append([
                    f'{hostname}.',
                    record_type,
                    f'{target}.',
                ])

        # Now format the whole thing into columnar data
        dnsrecords = format_columnar_data(dnsrecords)
        d = {
            'site': site,
            'dnsrecords': dnsrecords,
        }
        return render(request, 'dnsconf_reverse.jinja', d, content_type='text/plain')

    @action(detail=True, methods=['get', ], url_path='dnsconf/hosts')
    def dnsconf_hosts(self, request, pk=None):
        '''DNS configuration in /etc/hosts format (for CoreDNS)'''
        site = self.get_object()
        dnsrecords = []

        for networkdevice in site.networkdevice_set.all():
            for netinterface in networkdevice.networkinterface_set.all():
                for configuration in netinterface.networkinterfaceconfiguration_set.all():
                    ipaddress = configuration.ipaddress
                    if ipaddress is not None and ipaddress != '':
                        hostnames = [hostname.hostname for hostname in configuration.hostname_set.all()]
                        hostnames = ' '.join(hostnames)
                        dnsrecords.append([
                            ipaddress,
                            hostnames,
                        ])

        # Sort by IP Address for human sanity
        dnsrecords = sorted(dnsrecords, key=lambda x: socket.inet_aton(x[0]))

        # Now format the whole thing into columnar data
        dnsrecords = format_columnar_data(dnsrecords)

        d = {
            'site': site,
            'dnsrecords': dnsrecords,
            'utcnow': datetime.datetime.utcnow(),
        }
        return render(request, 'dnsconf_hosts.jinja', d, content_type='text/plain')

class NetworkDeviceFilterSet(filters.FilterSet):
    # Filter for "Is a webcam?" as well as various webcam flags
    webcam = filters.BooleanFilter(field_name='webcam', lookup_expr='isnull', exclude=True)
    webcam_is_enabled = filters.BooleanFilter(field_name='webcam__is_enabled', lookup_expr='exact')
    webcam_is_public = filters.BooleanFilter(field_name='webcam__is_public', lookup_expr='exact')
    webcam_is_dome = filters.BooleanFilter(field_name='webcam__is_dome', lookup_expr='exact')
    # Filter by Site code
    site = filters.CharFilter(field_name='site__code', lookup_expr='iexact')

    class Meta:
        model = NetworkDevice
        fields = {
        }

# ViewSets define the view behavior.
class NetworkDeviceViewSet(FlexFieldsModelViewSet):
    queryset = NetworkDevice.objects.all()
    queryset = queryset.select_related('site')
    queryset = queryset.select_related('puppetmachine')
    queryset = queryset.prefetch_related('networkinterface_set')
    queryset = queryset.prefetch_related('networkinterface_set__networkinterfaceconfiguration_set')
    queryset = queryset.prefetch_related('networkinterface_set__networkinterfaceconfiguration_set__hostname_set')
    serializer_class = NetworkDeviceSerializer
    permit_list_expands = [
        'site',
        'puppetmachine',
        'puppetmachine.facts',
        'puppetmachine.lcogtinstruments',
    ]
    filter_backends = (
        filters.DjangoFilterBackend,
    )
    filter_class = NetworkDeviceFilterSet

    # This is the main entrypoint into the API once we have valid data.
    # Wrap this operation in an atomic database transaction, so that any
    # failures in database operations (CREATE/UPDATE) on nested objects will
    # fail the entire API operation, without leaving any orphaned sub-objects
    # in the database.
    @transaction.atomic
    @mycontext('NetworkDeviceViewSet::perform_create')
    def perform_create(self, serializer):
        print(f'NetworkDeviceViewSet::perform_create: CREATE')
        return super().perform_create(serializer=serializer)

    # This is the main entrypoint into the API once we have valid data.
    # Wrap this operation in an atomic database transaction, so that any
    # failures in database operations (CREATE/UPDATE) on nested objects will
    # fail the entire API operation, without leaving any orphaned sub-objects
    # in the database.
    @transaction.atomic
    @mycontext('NetworkDeviceViewSet::perform_update')
    def perform_update(self, serializer):
        print(f'NetworkDeviceViewSet::perform_update: UPDATE')
        return super().perform_update(serializer=serializer)

    # This is the main entrypoint into the API once we have valid data.
    # Wrap this operation in an atomic database transaction, so that any
    # failures in database operations (CREATE/UPDATE) on nested objects will
    # fail the entire API operation, without leaving any orphaned sub-objects
    # in the database.
    @transaction.atomic
    @mycontext('NetworkDeviceViewSet::perform_destroy')
    def perform_destroy(self, instance):
        print(f'NetworkDeviceViewSet::perform_destroy: DELETE')

        # Remove the image for this device from AWS S3
        if instance.image is not None:
            instance.image.delete(save=False)

        # The on_delete=CASCADE option on the model takes care of the sub-objects
        return super().perform_destroy(instance=instance)

    @action(detail=True, methods=['get', ])
    def alive(self, request, pk=None):
        '''
        Run a simple fixed "ping" and determine whether this host is alive in a simple,
        quick, and not-very-reliable manner. A better test would try actually connecting
        to the host and running a command (for PuppetMachine hosts, expected to run Linux).
        But we don't do that, so this is just a stupid ping.
        '''
        # fetch database record
        networkdevice = self.get_object()

        # fetch hostname / ip address from database record
        target = networkdevice.primary_staticip
        if target is None:
            target = networkdevice.primary_hostname

        # whoops, the record is missing the sub-objects? What is going on?
        if target is None:
            data = make_simple_error(f'No IP Address or Hostname for NetworkDevice pk={networkdevice.pk}')
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # fixed ping command to check for aliveness
        cmd = [
            '/bin/ping',
            '-n',
            '-w',
            '10',
            '-i',
            '0.2',
            '-c',
            '3',
            '-l',
            '3',
            str(target),
        ]

        # Run the command, capturing all output into a single stream. Hard deadline of 15 seconds.
        timeout = 15
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        data = {
            'alive': proc.returncode == 0,
        }
        return Response(data=data)

    @action(detail=True, methods=['get', 'post', ])
    def bootmode(self, request, pk=None):
        '''Toggle the PuppetMachine.boot_mode database field for this NetworkDevice'''
        networkdevice = self.get_object()
        puppetmachine = None

        try:
            puppetmachine = networkdevice.puppetmachine
        except PuppetMachine.DoesNotExist as ex:
            data = make_simple_error(f'NetworkDevice(pk={networkdevice.pk}) is not Puppet managed')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # "GET" requests fetch the current boot mode
        if request.method == 'GET':
            data = {
                'boot_mode': puppetmachine.boot_mode,
            }
            return Response(data)

        # "POST" requests set the boot mode
        action = request.data.get('action', None)
        values = [name for (name, desc) in PuppetMachine.BOOT_MODE_CHOICES]

        # precondition: make sure the user sent an action value
        if action is None:
            data = make_simple_error(f'The "action" POST data parameter is required')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # precondition: make sure it is one of the acceptable valid values
        if action not in values:
            data = make_simple_error(f'The "action" value "{action}" is not supported (choose from: {",".join(values)})')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Boot History API: mark automatic rebuilds as complete
        if not request_is_internal(request):
            # previous state was "rebuild" and new state is "local", the rebuild is complete
            if puppetmachine.boot_mode.startswith('rebuild'):
                BuildHistory.objects.create(
                    puppetmachine=puppetmachine,
                    status='COMPLETE',
                )

        # save it
        puppetmachine.boot_mode = action
        puppetmachine.save()

        # return the new (updated) data
        data = {
            'boot_mode': puppetmachine.boot_mode,
        }
        return Response(data)

    @action(detail=True, methods=['get', ])
    def ping(self, request, pk=None):
        '''Run a "ping" to this network device and report the results'''
        # fetch this record from the database
        networkdevice = self.get_object()

        # fetch hostname / ip address from database record
        target = networkdevice.primary_staticip
        if target is None:
            target = networkdevice.primary_hostname

        # whoops, the record is missing the sub-objects? What is going on?
        if target is None:
            data = make_simple_error(f'No IP Address or Hostname for NetworkDevice pk={networkdevice.pk}')
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # deadline parameter (default: 15 seconds)
        try:
            deadline = int(request.GET.get('deadline', '15'))
            deadline = clamp(deadline, 5, 30)
        except Exception as ex:
            data = make_simple_error(f'''unable to parse deadline="{request.GET.get('deadline', '')}" as integer''')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # count parameter (default: 4 packets)
        try:
            count = int(request.GET.get('count', '4'))
            count = clamp(count, 1, 30)
        except Exception as ex:
            data = make_simple_error(f'''unable to parse count="{request.GET.get('count', '')}" as integer''')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # preload parameter (default: 2 packets)
        try:
            preload = int(request.GET.get('preload', '2'))
            preload = clamp(preload, 0, 3)
        except Exception as ex:
            data = make_simple_error(f'''unable to parse preload="{request.GET.get('preload', '')}" as integer''')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Build ping command with the following features:
        # - Numeric-only output (no DNS resolution)
        # - 15 second maximum execution time (deadline)
        # - 0.2 second (200ms) interval between sending packets
        # - 4 packets (maximum) will be sent (count 4)
        # - 2 packets sent immediately at startup (preload 2)
        cmd = [
            '/bin/ping',
            '-n',
            '-w',
            str(deadline),
            '-i',
            '0.2',
            '-c',
            str(count),
            '-l',
            str(preload),
            str(target),
        ]

        # Run the command, capturing all output into a single stream. Another hard
        # deadline on the execution time is added here too. This should never hit,
        # but will protect us just in case something else is going wrong in /bin/ping.
        # Also prevent the subprocess module from raising subprocess.CalledProcessError
        # when the /bin/ping program terminates incorrectly (cannot reach the device).
        timeout = (deadline + 5)
        timeout = clamp(timeout, 5, 40)
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        return Response(data=proc.stdout, content_type='text/plain')

    @action(detail=True, methods=['get', ])
    def ipmi_chassis_status(self, request, pk=None):
        '''IPMI chassis status'''
        networkdevice = self.get_object()
        return run_ipmitool(networkdevice, command=['chassis', 'status', ], timeout=15)

    @action(detail=True, methods=['get', ])
    def ipmi_power_status(self, request, pk=None):
        '''Use IPMI to retrieve the power status of a NetworkDevice'''
        networkdevice = self.get_object()
        return run_ipmitool(networkdevice, command=['power', 'status', ], timeout=15)

    @action(detail=True, methods=['post', ])
    def ipmi_power_on(self, request, pk=None):
        '''Use IPMI to power on a NetworkDevice'''
        networkdevice = self.get_object()
        return run_ipmitool(networkdevice, command=['power', 'on', ], timeout=15)

    @action(detail=True, methods=['post', ])
    def ipmi_power_off(self, request, pk=None):
        '''Use IPMI to power off a NetworkDevice'''
        networkdevice = self.get_object()
        return run_ipmitool(networkdevice, command=['power', 'off', ], timeout=15)

    @action(detail=True, methods=['get', 'post'])
    def puppet_agent_test(self, request, pk=None):
        '''Trigger a "puppet agent --test" run immediately on this NetworkDevice'''
        # Fetch record from database
        networkdevice = self.get_object()

        # POST request starts a Puppet Agent run immediately
        if request.method == 'POST':
            queue = django_rq.get_queue()
            job = queue.enqueue(run_puppet_agent_test, networkdevice_id=networkdevice.pk, job_timeout=3600)
            data = {
                'job_id': job.id,
                'job_timeout': job.timeout,
            }
            return Response(data)

        # GET request polls for completion
        if request.method == 'GET':
            job_id = request.GET.get('job_id', None)
            if job_id is None:
                data = make_simple_error(f'GET parameter job_id is required')
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            # Fetch RQ Job by UUID
            queue = django_rq.get_queue()
            job = queue.fetch_job(job_id)
            if job is None:
                data = make_simple_error(f'No RQ Job with job_id={job_id} found')
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'status': job.get_status(),
                'result': job.result,
            }
            return Response(data)

class UnrecognizedPXEDeviceFilterSet(filters.FilterSet):
    class Meta:
        model = UnrecognizedPXEDevice
        fields = {
            'mac': [ 'exact', ],
            'ipaddress': [ 'exact', ],
            'created_at': [ 'exact', 'lte', 'gte', ],
        }

# ViewSets define the view behavior.
class UnrecognizedPXEDeviceViewSet(FlexFieldsModelViewSet):
    queryset = UnrecognizedPXEDevice.objects.all()
    serializer_class = UnrecognizedPXEDeviceSerializer
    permit_list_expands = [
        'site',
    ]
    filter_backends = (
        filters.DjangoFilterBackend,
    )
    filter_class = UnrecognizedPXEDeviceFilterSet

class BootHistoryFilterSet(filters.FilterSet):
    # Filter by Site code
    site = filters.CharFilter(field_name='puppetmachine__networkdevice__site__code', lookup_expr='iexact')

    class Meta:
        model = BootHistory
        fields = {
            'created_at': [ 'exact', 'lte', 'gte', ],
            'boot_mode': [ 'exact', ],
        }

class BootHistoryViewSet(FlexFieldsModelViewSet):
    queryset = BootHistory.objects.all()
    serializer_class = BootHistorySerializer
    permit_list_expands = [
        'puppetmachine',
        'networkdevice',
    ]
    filter_backends = (
        filters.DjangoFilterBackend,
    )
    filter_class = BootHistoryFilterSet

class BuildHistoryFilterSet(filters.FilterSet):
    class Meta:
        model = BuildHistory
        fields = {
            'created_at': [ 'exact', 'lte', 'gte', ],
            'status': [ 'exact', ],
        }

class BuildHistoryViewSet(FlexFieldsModelViewSet):
    queryset = BuildHistory.objects.all()
    serializer_class = BuildHistorySerializer
    permit_list_expands = [
        'puppetmachine',
        'networkdevice',
    ]
    filter_backends = (
        filters.DjangoFilterBackend,
    )
    filter_class = BuildHistoryFilterSet

# vim: set ts=4 sts=4 sw=4 et tw=120:
