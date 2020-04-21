#!/usr/bin/python3

import json
import os
from optparse import OptionParser

import svgwrite
from svgwrite import mm, px   

def get_hosts(netmap):
    hosts = list(netmap['machines'])
    hosts.sort()
    return hosts

def get_switches_left(netmap):
    hosts = list(netmap['switches'])
    hosts.sort()
    return hosts[0::2]

def get_switches_right(netmap):
    hosts = list(netmap['switches'])
    hosts.sort()
    return hosts[1::2]

def init_side_pane(netmap, items):
    meta = {
        'max_width': 0,
        'max_height': 0,
        'count' : len(items),
        'items': items
    }  
    for item in items:
        meta[item] = {}
        meta[item]['width'] = len(item)
        meta[item]['vlans'] = {}
        meta[item]['ports'] = []
        for vlan in netmap['switches'][item]['vlans']:
            meta[item]['vlans'][vlan] = {'ports': []}
            for port in netmap['switches'][item]['vlans'][vlan]:
                if len(item) > meta[item]['width']:
                    meta[item]['width'] = len(item)
                meta[item]['vlans'][vlan]['ports'].append(port)
                meta[item]['ports'].append(port)
                meta[item][port] = {}
        meta[item]['height'] = len(netmap['switches'][item]['ports'])+len(netmap['switches'][item]['vlans'])
        if meta[item]['width'] > meta['max_width']:
            meta['max_width'] = meta[item]['width']
        if meta[item]['height'] > meta['max_height']:
           meta['max_height'] = meta[item]['height']        
    return meta

def init_center_pane(netmap, items, peers):
    meta = {
        'max_width': 0,
        'max_height': 0,
        'count' : len(items),
        'items': items
    }  
    for item in items:
        meta[item] = {}
        meta[item]['width'] = len(item)
        meta[item]['ports_left'] = []
        meta[item]['ports_right'] = []
        meta[item]['vlans'] = {}
        meta[item]['ports'] = []
        port_left_max_width=0
        port_right_max_width=0
        for vlan in netmap['machines'][item]['vlans']:
            meta[item]['vlans'][vlan] = {'ports': []}        
            for port in netmap['machines'][item]['vlans'][vlan]:            
                if netmap['machines'][item]['ports'][port]['chassis'] in peers['left']:
                    meta[item]['ports_left'].append(port)
                    meta[item]['ports'].append(port)
                    meta[item]['vlans'][vlan]['ports'].append(port)
                    meta[item][port] = {'align': 'left'}
                    if len(port) > port_left_max_width:
                        port_left_max_width = len(port)
                if netmap['machines'][item]['ports'][port]['chassis'] in peers['right']:
                    meta[item]['ports_right'].append(port)
                    meta[item]['ports'].append(port)
                    meta[item][port] = {'align': 'right'} 
                    if len(port) > port_right_max_width:
                        port_right_max_width = len(port)

        if meta[item]['width'] < port_right_max_width + port_left_max_width:
            meta[item]['width'] = port_right_max_width + port_left_max_width

        if meta[item]['width'] > meta['max_width']:
            meta['max_width'] = meta[item]['width']            

        meta[item]['height'] = max(len(meta[item]['ports_left']),
                                   len(meta[item]['ports_right'])
                                ) + len(netmap['machines'][item]['vlans'])
        if meta[item]['height'] > meta['max_height']:
            meta['max_height'] = meta[item]['height']
    return meta

def prepare_topology_metadata(netmap):
    meta = {}
    items = {}
    items['left'] = get_switches_left(netmap)
    items['right'] = get_switches_right(netmap)
    items['center'] = get_hosts(netmap)
    meta['left'] = init_side_pane( netmap, items['left'])
    meta['right'] = init_side_pane( netmap, items['right'])
    meta['center'] = init_center_pane( netmap, items['center'], items )
    return meta

def prepare_placement_metadata(meta, options):
    max_height = 0
    for side in ['left', 'center', 'right']:
        height = (meta[side]['max_height'] * options['port_height'] + options['item_label_height'] + options['item_hspace'])*meta[side]['count']
        if height > max_height:
            max_height = height
    
    meta['left']['x'] = options['img_left_padding']
    meta['center']['x'] = meta['left']['x'] + meta['left']['max_width']* options['col_width'] + options['item_vspace']
    meta['right']['x'] = meta['center']['x'] + meta['center']['max_width'] * options['col_width'] + options['item_vspace']
    for side in ['left', 'center', 'right']:
        meta[side]['box_height'] = max_height / meta[side]['count']
        y = 0
        for item in meta[side]['items']:
            box_x = meta[side]['x']
            box_y = meta[side]['box_height']*y
            meta[side][item]['width'] = meta[side]['max_width'] * options['col_width']
            meta[side][item]['height'] = meta[side][item]['height'] * options['port_height'] + options['item_label_height']                
            meta[side][item]['x'] = box_x
            meta[side][item]['y'] = box_y + (meta[side]['box_height'] - meta[side][item]['height']) / 2
            if side == 'center':
                for col in ['left', 'right']:
                    dy = 0
                    for port in meta[side][item]['ports_' + col]:
                        meta[side][item][port]['width'] = (meta[side]['max_width'] / 2) * options['col_width']
                        meta[side][item][port]['height'] = options['port_height']
                        meta[side][item][port]['y'] = meta[side][item]['y'] + options['item_label_height'] + dy * meta[side][item][port]['height']                        
                        meta[side][item][port]['anchor_y'] = meta[side][item][port]['y'] + meta[side][item][port]['height'] / 2
                        if col == 'left':
                            meta[side][item][port]['x'] = meta[side][item]['x']
                            meta[side][item][port]['anchor_x'] = meta[side][item]['x']
                        if col == 'right':
                            meta[side][item][port]['x'] = meta[side][item]['x'] + (meta[side]['max_width'] / 2) * options['col_width']
                            meta[side][item][port]['anchor_x'] = meta[side][item][port]['x'] + meta[side][item][port]['width']
                        dy += 1                                                
            else:
                dy = 0
                for port in meta[side][item]['ports']:
                    meta[side][item][port]['width'] = meta[side]['max_width'] * options['col_width']
                    meta[side][item][port]['height'] = options['port_height']
                    meta[side][item][port]['x'] = meta[side][item]['x'] 
                    meta[side][item][port]['y'] = meta[side][item]['y'] + options['item_label_height'] + dy * meta[side][item][port]['height']                    
                    meta[side][item][port]['anchor_y'] = meta[side][item][port]['y'] + meta[side][item][port]['height'] / 2
                    if side == 'left':
                        meta[side][item][port]['anchor_x'] = meta[side][item]['x'] + meta[side][item][port]['width']
                    if side == 'right':
                        meta[side][item][port]['anchor_x'] = meta[side][item]['x']
                    dy += 1                
            y += 1
    return meta

def port_color(netmap, item, port):
    if item in netmap['machines']:
        port_data = netmap['machines'][item]['ports'][port]
    if item in item in netmap['switches']:
        port_data = netmap['switches'][item]['ports'][port]
    if 'vlan' in port_data:
        vlan_id = int(port_data['vlan'])
    else:
        vlan_id = 0
    return vlan_color(vlan_id)

def vlan_color(vlan_id):
    if vlan_id == 0:
        return 'gray'
    rev = int(str(vlan_id)[::-1])
    color = {}
    color['r'] = (rev * (( rev / 10 ) % 10)) % 256
    color['g'] = (rev * (( rev / 100 ) % 10)) % 256
    color['b'] = (rev * (( rev / 1000 ) % 10)) % 256
    return svgwrite.rgb(color['r'], color['g'], color['b'])

def render_svg(netmap, outfile):
    dwg = svgwrite.Drawing(filename=outfile, debug=True)
    shapes = dwg.add(dwg.g(id='shapes'))
    options = {
        'col_width' : 2.2,
        'port_height' : 5,
        'item_hspace' : 1,
        'item_vspace' : 100,
        'img_left_padding' : 10,
        'item_label_height' : 5,
        'format' : {
            'line_width': 3,
            'left' : {
                'item' : {
                    'fill': 'none',
                    'stroke': 'black',
                },
                'item_label' : {
                    'text_anchor': 'middle'
                },
                'port' : {
                    'stroke': 'black'
                },
                'port_label' : {
                    'text_anchor': 'middle'
                },
            },
            'center' : {
                'item' : {
                    'fill': 'none',
                    'stroke': 'black'
                },
                'item_label' : {
                    'text_anchor': 'middle'
                },                
                'port' : {
                    'stroke': 'black'
                },
                'port_label' : {
                    'text_anchor': 'middle'
                },                
            },
            'right' : {
                'item' : {
                    'fill': 'none',
                    'stroke': 'green'
                },
                'item_label' : {
                    'text_anchor': 'middle'
                },
                'port' : {
                    'stroke': 'black'
                },
                'port_label' : {
                    'text_anchor': 'middle'
                },                
            },
        }
    }
    topology = prepare_topology_metadata(netmap)
    meta = prepare_placement_metadata(topology, options)
    unit = mm
    for side in ['left', 'center', 'right']:
        for item in meta[side]['items']:
            rect = dwg.rect(insert = (
                                meta[side][item]['x'] * unit, 
                                meta[side][item]['y'] * unit), 
                            size = (
                                meta[side][item]['width'] * unit, 
                                meta[side][item]['height'] * unit),
                            **options['format'][side]['item'])
            label = dwg.text(item, 
                        insert = (
                            (meta[side][item]['x'] + meta[side][item]['width'] / 2) * unit, 
                            (meta[side][item]['y'] + options['item_label_height'])*unit),
                        **options['format'][side]['item_label']
                    )
            shapes.add(rect)
            shapes.add(label)
            for port in meta[side][item]['ports']:
                dwg_opts = options['format'][side]['port'].copy()
                if 'fill' not in dwg_opts:
                    dwg_opts['fill'] = port_color(netmap, item, port)
                rect = dwg.rect(insert=(meta[side][item][port]['x'] * unit, meta[side][item][port]['y'] * unit), 
                        size=(meta[side][item][port]['width'] * unit, meta[side][item][port]['height'] * unit),
                        **dwg_opts)
                label = dwg.text(port, 
                            insert=(
                                (meta[side][item][port]['x'] + meta[side][item][port]['width'] / 2 ) * unit, 
                                (meta[side][item][port]['y'] + options['item_label_height']) * unit),
                            **options['format'][side]['port_label']
                        )
                shapes.add(rect)
                shapes.add(label)
                for link in netmap['links']:
                    if link['source_host'] == item and link['source_port'] == port:
                        for dst_side in ['left', 'center', 'right']:
                            for dst_item in meta[dst_side]['items']:
                                if dst_item == link['destination_host']:
                                    for dst_port in meta[dst_side][dst_item]['ports']:
                                        if dst_port == link['destination_port']:
                                            if 'line_stroke' not in options['format']:
                                                stroke = port_color(netmap, item, port)
                                            else:
                                                stroke = options['format']['line_stroke']
                                            line = dwg.line(
                                                start = (
                                                    meta[side][item][port]['anchor_x'] * unit,
                                                    meta[side][item][port]['anchor_y'] * unit,
                                                ),
                                                end = (
                                                    meta[dst_side][dst_item][dst_port]['anchor_x'] * unit,
                                                    meta[dst_side][dst_item][dst_port]['anchor_y'] * unit,
                                                ),
                                                stroke_width = options['format']['line_width'],
                                                stroke = stroke
                                            )
                                            shapes.add(line)                                            
    dwg.save()

def main(options):
    netmap = {}
    with open(options.infile) as f:
        netmap = json.load(f)
    render_svg(netmap, options.outfile)

if __name__ == "__main__":
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input",
                        action="store", type="string", dest="infile", default='netmap.json', help="Input file")    
    parser.add_option("-o", "--output",
                        action="store", type="string", dest="outfile", default='netmap.svg', help="Output file")
    (options, args) = parser.parse_args()    
    main(options)