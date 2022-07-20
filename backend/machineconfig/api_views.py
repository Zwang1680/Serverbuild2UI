from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

import subprocess
import ipaddress
import requests

class MyArgumentError(Exception):
    pass

def parse_boolean(value):
    orig_value = str(value)

    value = orig_value.lower()
    if value in ['t', 'true', 'y', 'yes', '1', ]:
        return True
    if value in ['f', 'false', 'n', 'no', '0', ]:
        return False

    raise ValueError(f'Unable to parse "{orig_value}" as a Boolean (true/false) value')

def clamp(n, lower_bound, upper_bound):
    return max(lower_bound, min(n, upper_bound))

def make_simple_error(message):
    data = {
        'error': message,
    }
    return data

@api_view(['GET',], )
@permission_classes([permissions.AllowAny, ])
def lcogtinstruments(request):
    '''
    Get all lcogtinstruments fact data from PuppetDB
    '''
    url = 'http://core.lco.gtn:8080/pdb/query/v4/facts/lcogtinstruments'
    response = requests.get(url)
    response.raise_for_status()
    return Response(response.json())

@api_view(['GET', ], )
@permission_classes([permissions.AllowAny, ])
def tools_ping(request, target):
    '''
    Run the /bin/ping command to perform a simple connectivity test. May not work
    for all hosts, depending on whether or not they block ICMP.

    No target IP Address / Hostname checking or validation is performed. This is a
    totally open remote hole into the LCO-internal network.
    '''
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
    data = {
        'command': cmd,
        'stdout': proc.stdout,
        'returncode': proc.returncode,
    }
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET', ], )
@permission_classes([permissions.AllowAny, ])
def tools_traceroute(request, target):
    cmd = [
        '/usr/bin/traceroute',
        '--sim-queries=10000',
        '--extensions',
        '--as-path-lookups',
        str(target)
    ]

    timeout = 45
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    data = {
        'command': cmd,
        'stdout': proc.stdout,
        'returncode': proc.returncode,
    }
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET', ], )
@permission_classes([permissions.AllowAny, ])
def tools_host(request, target):
    '''
    Run the /usr/bin/host command to perform a human-readable DNS lookup. No target
    IP Address / Hostname checking or validation is performed: this is a totally
    open remote hole into the LCO-internal DNS system.
    '''
    # verbose parameter (default: false)
    try:
        verbose = request.GET.get('verbose', 'false')
        verbose = parse_boolean(verbose)
    except ValueError as ex:
        data = make_simple_error(f'unable to parse "verbose={verbose}" as boolean (true/false)')
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # build command
    cmd = [ '/usr/bin/host', '-W', '3', ]
    if verbose:
        cmd.append('-v')

    cmd.append(str(target))

    # run command
    timeout = 5
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)

    # return response to user
    data = {
        'command': cmd,
        'stdout': proc.stdout,
        'returncode': proc.returncode,
    }
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(['GET', ], )
@permission_classes([permissions.AllowAny, ])
def tools_dig(request, target):
    '''
    Run the /usr/bin/dig command to perform an advanced DNS lookup. No target
    IP Address / Hostname checking or validation is performed: this is a totally
    open remote hole into the LCO-internal DNS system.
    '''
    cmd = [
        '/usr/bin/dig',
    ]

    # automatically figure out the target type and whether we need to use the
    # "-x" option for a simple reverse lookup (in-addr.arpa and PTR record type)
    try:
        addr = ipaddress.ip_address(target)
        cmd.append('-x')
    except ValueError as ex:
        pass

    # append target
    cmd.append(str(target))

    # run command
    timeout = 5
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)

    # return response to user
    data = {
        'command': cmd,
        'stdout': proc.stdout,
        'returncode': proc.returncode,
    }
    return Response(data=data, status=status.HTTP_200_OK)

# vim: set ts=4 sts=4 sw=4 et tw=120:
