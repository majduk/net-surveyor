#!/usr/bin/python3

import json
import os
from optparse import OptionParser

def get_ports(netmap):
    ports = []
    for host in get_hosts(netmap):
        for port in netmap['machines'][host]['ports']:
            if port not in ports:
                ports.append(port)
    ports.sort()
    return ports

def get_hosts(netmap):
    hosts = list(netmap['machines'])
    hosts.sort()
    return hosts

def get_port_data(netmap, host, port):
    data = {}
    keys = ['chassis', 'port', 'vlan', 'descr']
    pdata = netmap['machines'][host]['ports'][port]
    try:
        for key in keys:
            data[key] = pdata[key]
    except KeyError:
        pass
    return str(data)

def write_header(f):
    f.write("<html><body>\n")

def write_footer(f):
    f.write("</body></html>")

def write_table_header(f, ports):
    f.write("<table border=1><tr>")
    f.write("<td>Hostname</td>")
    for port in ports:
        f.write("<td>" + port + "</td>")
    f.write("</tr>\n")

def write_table_footer(f):
    f.write("</tr></table>\n")

def write_table_row(f, netmap, host, ports):
    f.write("<tr>")
    f.write("<td>" + host + "</td>")
    for port in ports:
        try:
            f.write("<td>" + get_port_data(netmap, host, port) + "</td>")
        except KeyError:
                f.write("<td>" + "Not connected" + "</td>")
    f.write("</tr>\n")    

def render_html(netmap, outfile):
    ports = get_ports(netmap)
    hosts = get_hosts(netmap)
    with open(outfile, 'w') as f:
        write_header(f)
        write_table_header(f, ports)
        for host in hosts:
            write_table_row(f, netmap, host, ports)
        write_table_footer(f)
        write_footer(f)

def main(options):
    netmap = {}
    with open(options.infile) as f:
        netmap = json.load(f)
    render_html(netmap, options.outfile) 

if __name__ == "__main__":
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input",
                        action="store", type="string", dest="infile", default='netmap.json', help="Input file")    
    parser.add_option("-o", "--output",
                        action="store", type="string", dest="outfile", default='netmap.html', help="Output file")
    (options, args) = parser.parse_args()    
    main(options)