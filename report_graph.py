#!/usr/bin/python3

import json
import os
from optparse import OptionParser
import networkx as nx
import matplotlib.pyplot as plt

def get_hosts(netmap):
    hosts = list(netmap['machines'])
    hosts.sort()
    return hosts

def get_switches(netmap):
    hosts = list(netmap['switches'])
    hosts.sort()
    return hosts

def render_graph(netmap, outfile):
    colors = {'host': 'blue',
              'switch': 'green',
              'iface': 'red',
              'port': 'red',
    }

    G = nx.Graph()
    color_map = []
    label_map = {}
    for host in get_hosts(netmap):
        G.add_node(host)
        color_map.append(colors['host'])
        label_map[host] = host
        for port in netmap['machines'][host]:
            G.add_node(host + port)
            color_map.append(colors['iface'])
            G.add_edge(host, host + port)
            label_map[host + port] = port
    for switch in get_switches(netmap):
        G.add_node(switch)
        color_map.append(colors['switch'])
    for link in netmap['links']:
        G.add_node(link['destination_host'] + link['destination_port'])
        color_map.append(colors['port'])
        G.add_edge(link['destination_host'], link['destination_host'] + link['destination_port'])
        G.add_edge(link['source_host'] + link['source_port'], link['destination_host'] + link['destination_port'])
    nx.draw(G, labels=label_map, node_color=color_map, with_labels=True)
    #plt.savefig(outfile)
    plt.show()

def main(options):
    netmap = {}
    with open(options.infile) as f:
        netmap = json.load(f)
    render_graph(netmap, options.outfile) 

if __name__ == "__main__":
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input",
                        action="store", type="string", dest="infile", default='netmap.json', help="Input file")    
    parser.add_option("-o", "--output",
                        action="store", type="string", dest="outfile", default='netmap.png', help="Output file")
    (options, args) = parser.parse_args()    
    main(options)