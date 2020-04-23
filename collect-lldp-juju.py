#!/usr/bin/python3

import json
import os
import shutil
import tempfile
import subprocess
from optparse import OptionParser

def get_model_machies():
    raw = subprocess.check_output('juju machines --format json',shell=True)
    ret = []
    json_machines = json.loads(raw)
    for id in json_machines['machines']:
        name = json_machines['machines'][id]['display-name']
        ret.append( (id,name) )
    return ret

def write_collector_script(install_lldp = True):
    ftmp, ftmpname = tempfile.mkstemp()
    header = "#!/bin/bash\n"
    install = """
    for interface in `ls /sys/kernel/debug/i40e`
    do echo "lldp stop" > /sys/kernel/debug/i40e/${interface}/command
    done
    apt install lldpd -y;
    """
    collect = "lldpcli show neighbors details -f json > /tmp/lldp_output.json\n"
    body = header
    if install_lldp:
        body += install
        body += "\n"
    body += collect
    os.write(ftmp,body.encode('utf-8'))
    os.close(ftmp)
    return ftmpname

def copy_script(machine, script_name):
    subprocess.run("juju scp {script_name} {machine}:{script_name}".format(machine = machine, script_name = script_name), shell = True)

def run_script(machine, script_name):
    subprocess.run("juju ssh {machine} \"chmod 700 {script_name}; sudo {script_name}; rm {script_name}\""
                   .format(machine = machine, script_name = script_name), shell = True)

def collect_data(machine_id, hostname, work_dir):
    subprocess.run("juju scp {machine_id}:/tmp/lldp_output.json {work_dir}/{hostname}.json"
                   .format(machine_id = machine_id, hostname = hostname, work_dir = work_dir), shell = True)

def main(options):
    if os.path.isdir(options.work_dir):
        shutil.rmtree(options.work_dir)
        os.mkdir(options.work_dir)
    script_name = write_collector_script(options.install_lldp)
    for machine in get_model_machies():
        id = machine[0]
        hostname = machine[1]
        copy_script(id, script_name)
        run_script(id, script_name)
        collect_data(id, hostname, options.work_dir)
    os.remove(script_name)

if __name__ == "__main__":
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dir",
                        action="store", type="string", dest="work_dir", default="/tmp/lldp", help="Output directory")
    parser.add_option("-i", "--install",
                        action="store_true",  dest="install_lldp", default=False, help="Install LLDP tools first")                        
    (options, args) = parser.parse_args()    
    main(options)