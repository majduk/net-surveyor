#!/usr/bin/python3

import json
import os
from optparse import OptionParser

def init_netmap(netmap):
    netmap['vlans'] = []
    netmap['machines'] = {}
    netmap['switches'] = {}
    netmap['links'] = []

def add_vlan(netmap, vlan):
    if vlan not in netmap['vlans']:
        netmap['vlans'].append(vlan)

def add_switch_port(netmap, switch, pdata):
    if switch not in netmap['switches']:
        netmap['switches'][switch] = {}
    if 'ports' not in netmap['switches'][switch]:
        netmap['switches'][switch]['ports'] = {}
    if pdata['port'] not in netmap['switches'][switch]['ports']:
        netmap['switches'][switch]['ports'][pdata['port']] = pdata
    if 'vlans' not in netmap['switches'][switch]:
        netmap['switches'][switch]['vlans'] = {}
    if 'vlan' in pdata:
        vlan_id = pdata['vlan']
    else:
        vlan_id = 'untagged'
    if vlan_id not in netmap['switches'][switch]['vlans']:
        netmap['switches'][switch]['vlans'][vlan_id] = []
    netmap['switches'][switch]['vlans'][vlan_id].append(pdata['port'])        

def add_host_port(netmap, hostname, ifname, pdata):
    if hostname not in netmap['machines']:
        netmap['machines'][hostname] = {}
    if 'ports' not in netmap['machines'][hostname]:
        netmap['machines'][hostname]['ports'] = {}
    if ifname not in netmap['machines'][hostname]['ports']:
        netmap['machines'][hostname]['ports'][ifname] = pdata    
    if 'vlans' not in netmap['machines'][hostname]:
       netmap['machines'][hostname]['vlans'] = {}
    if 'vlan' in pdata:
       vlan_id = pdata['vlan']
    else:
       vlan_id = 'untagged'
    if vlan_id not in netmap['machines'][hostname]['vlans']:
       netmap['machines'][hostname]['vlans'][vlan_id] = []
    netmap['machines'][hostname]['vlans'][vlan_id].append(ifname)

def add_link(netmap, hostname, host_port, switch_name, switch_port):
    link = {'source_host': hostname, 
            'source_port': host_port, 
            'destination_host': switch_name, 
            'destination_port': switch_port, 
            }
    netmap['links'].append(link)

def parse_machine_file(netmap, work_dir, fname):
    hostname=fname.split('.')[0]
    with open(work_dir + "/" + fname) as f:
        data = json.load(f)
        for iface in data['lldp']['interface']:
            for ifname in iface.keys():
                iface_lldp = iface[ifname]
                pdata = {}
                pdata['raw'] = iface_lldp
                pdata['descr'] = iface_lldp['port']['descr']
                pdata['port'] = iface_lldp['port']['id']['value']
                if 'vlan' in iface_lldp:
                    vid = iface_lldp['vlan']['vlan-id']
                    pdata['vlan'] = vid
                    add_vlan(netmap, vid)
                for chassis_name in iface_lldp['chassis'].keys():
                    pdata['chassis'] = chassis_name
                    add_switch_port(netmap, chassis_name, pdata)
                add_host_port(netmap, hostname, ifname, pdata)
                add_link(netmap, hostname, ifname, chassis_name, pdata['port'])

def populate_netmap(netmap, work_dir):
    for fname in os.listdir(work_dir):
        parse_machine_file(netmap, work_dir, fname)

def main(options):
    netmap = {}
    init_netmap(netmap)
    populate_netmap(netmap, options.work_dir)
    with open(options.outfile, 'w') as outfile:
        json.dump(netmap, outfile)
    

if __name__ == "__main__":
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dir",
                        action="store", type="string", dest="work_dir", default="/tmp/lldp", help="Input directory")
    parser.add_option("-o", "--output",
                        action="store", type="string", dest="outfile", default='netmap.json', help="Output file")
    (options, args) = parser.parse_args()    
    main(options)

