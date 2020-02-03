#!/usr/bin/env python2.7

from netaddr import iter_iprange
import itertools
import json
import os
import pypureomapi
import re
import sys

KEYNAME = 'defomapi'
BASE64_ENCODED_KEY = 't6VuA3SIHcKaZWRuWkSOlw=='
dhcp_server_ip = '127.0.0.1'
port = 7911 # Port of the omapi service
OMAPI_OP_UPDATE = 3
DHCP_DIR = '/usr/pkg/etc/dhcp/' if os.path.isdir('/usr/pkg/etc/dhcp/') else '/etc/dhcp/'

def discoverRange(configFile):

    reg_range = re.compile('range\s(.*?);')
    reg_name = re.compile('#= (.*?) =#')
    ranges = []
    with open(configFile, 'r') as f:
        for key, group in itertools.groupby(f, lambda line: line.startswith('\n')):
            if not key:
                subnet_info = list(group)
                name = [m.group(1) for l in subnet_info for m in [reg_name.search(l)] if m]
                range_list = [m.group(1) for l in subnet_info for m in [reg_range.search(l)] if m]
                if range_list:
                    for num, range in enumerate(range_list):
                        ip_start = range.split(' ')[0]
                        ip_end = range.split(' ')[1]
                        ips = list(iter_iprange(ip_start, ip_end, step=1))
                        myname = 'IP Range {0}'.format(str(num))
                        if num < len(name):
                            myname = name[num]
                        ranges.append({'{#NAME}': myname, '{#RANGE}': '{0}-{1}'.format(ip_start, ip_end), '{#TOTAL}': len(ips)})
    return ranges

def checkRange(ipsList, ip_type):

    ip_start = ipsList.split('-')[0]
    ip_end = ipsList.split('-')[1]
    ips = list(iter_iprange(ip_start, ip_end, step=1))
    # man 8 dhcpd.conf
    leases_states = {
            1: 'free',
            2: 'active',
            3: 'expired',
            4: 'released',
            5: 'abandoned',
            6: 'reset',
            7: 'backup',
            8: 'reserved',
            9: 'bootp'
            }
    results = {
            'Total': len(ips),
            'free': 0,
            'active': 0,
            'expired': 0,
            'abandoned': 0,
            'reset': 0,
            'backup': 0,
            'reserved': 0,
            'bootp': 0,
            'released': 0
            }

    o = pypureomapi.Omapi(dhcp_server_ip, port, KEYNAME, BASE64_ENCODED_KEY)
    for ip in ips:
        msg = pypureomapi.OmapiMessage.open('lease')
        msg.obj.append(('ip-address', pypureomapi.pack_ip(str(ip))))
        response = o.query_server(msg)
        if response.opcode != OMAPI_OP_UPDATE:
            print 'ZBX_NOTSUPPORTED'
        # Need to dig for the key error thingy
        try:
            state = ord(response.obj[0][1][-1:])
            results[leases_states[state]] += 1
        except KeyError:
            print 'ZBX_NOTSUPPORTED'

    print(results[ip_type])

if __name__ == "__main__":

    if len(sys.argv) < 2:
        if os.path.isdir(DHCP_DIR + 'conf.d/'):
            configIncludeFiles = filter(lambda x: x.endswith('.conf'), os.listdir(DHCP_DIR + 'conf.d/'))
            for item in enumerate(configIncludeFiles):
                configIncludeFiles[item[0]]=DHCP_DIR + 'conf.d/' + item[1]
        configIncludeFiles.append(DHCP_DIR + 'dhcpd.conf')

        ranges_dict = {}
        i=[]
        for configFile in configIncludeFiles:
            i = i + discoverRange(configFile)
        ranges_dict['data'] = i
        sys.exit(json.dumps(ranges_dict))
    else:
        sys.exit(checkRange(sys.argv[1], sys.argv[2]))
