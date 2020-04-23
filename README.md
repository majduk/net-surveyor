# NET-SURVEYOR

## About Net-Surveyor
Net-Surveyor is an LLDP based tool which purpose is to collect, agggregate and visualise network topology data from cloud environment, thus simplifying network configuration and troubleshooting.

Net-Surveyor bases on [Link Layer Doscovery Protocol](https://en.wikipedia.org/wiki/Link_Layer_Discovery_Protocol) - LLDP - data about VLANs, switch port connectivity and link aggregation.

## Usage

Net-Surveyor works with multiple sources of LLDP data. Currently the preferred way is using [juju](https://jaas.ai/) and [magpie](https://jaas.ai/u/openstack-charmers-next/magpie).

The tool generates 3 types of reports:
- HTML web page with a table of all machines and interfaces with LLDP data in appropriate cells
- SVG network topology map with the same information as above
- Python NetworkX graph

### Juju 

Net-Surveyor can collect LLDP data from an existing juju environment. Please note that it will install LLDP on all the machines.

1. Clone the Net-Surveyor repository
2. Collect LLDP data:
```
./collect-lldp-juju.py -i 
```
This collects the data by default into `/tmp/lldp/`. `-i` installs LLDP on the machines. Note that if this is fresh LLDP install, this step may need to be repeated as LLDP data is collected over time, based on incoming LLDP PDUs.

3. Build topology from the collected data:
```
./build_netmap.py -o netmap.json
```
This step merges the collected data into single JSON file.

4. Create report:
```
./report_html.py -i netmap.json -o netmap.html
```

### Juju and magpie

1. Create a [juju](https://jaas.ai/) [magpie](https://jaas.ai/u/openstack-charmers-next/magpie) bundle for your environment. Magpie charm can be deployed on both bare metal machines and containers. Make sure to enable LLDP collection on bare metal machines:
```
series: "bionic"
machines:
  '1':
    constraints: tags=foundation-nodes
  '2': 
    constraints: tags=foundation-nodes
services:
  magpie-bare:
    charm: "cs:~openstack-charmers-next/magpie"
    series: "bionic"
    num_units: 2
    constraints: spaces=oam-space
    bindings:
      "": oam-space
    options:
      check_dns: true
      check_iperf: false
      check_bonds: "bond0,bond1,bond2"
      use_lldp: true                 # required to be true
      check_port_description: false
    to:
      - 1
      - 2
```
2. Deploy the bundle:
```
juju deploy ./magpie-bundle.yaml
```
3. Wait for the bundle to deploy
4. Clone the Net-Surveyor repository
5. Collect LLDP data:
```
./collect-lldp-juju.py
```
This collects the data by default into `/tmp/lldp/`

6. Build topology from the collected data:
```
./build_netmap.py -o netmap.json
```
This step merges the collected data into single JSON file.

7. Create report:
```
./report_html.py -i netmap.json -o netmap.html
```

### SSH

1. Create txt fle conatining hostnames of all machines to connect to, eg: `machines.txt`
2. Collect LLDP data:
```
./collect-lldp-ssh.sh machines.txt
```
This collects the data by default into `/tmp/lldp/`

3. Build topology from the collected data:
```
./build_netmap.py -o netmap.json
```
This step merges the collected data into single JSON file.

4. Create report:
```
./report_html.py -i netmap.json -o netmap.html
```


## Future work

1. Update and publish plugin to collect [MAAS](maas.io) comissioning data.
2. Improve SVG graph to group host interfaces into VLANs
3. Add VLAN and host filtering for report generation
4. Create Net-Surveyor SNAP
5. Create Net-Surveyor server and integrate with Magpie for single bundle deployment

## Bugs and feature requests

Use issues reporting feature in this repository to report bugs and feature requests.

All contributions are heartily welcome.
