#!/usr/bin/env bash
input_file=${1:-machines.txt}
if [ ! -f $input_file ];then
  echo "Missing machines list"
  exit 1
fi
download_dir='/tmp/lldp'

rm -rf $download_dir
mkdir -p $download_dir
script=$(mktemp)

cat > $script << "EOF"
#!/bin/bash
for interface in `ls /sys/kernel/debug/i40e`
  do echo "lldp stop" > /sys/kernel/debug/i40e/${interface}/command
done

apt install lldpd -y
sleep 10
lldpcli show neighbors details -f json > /tmp/lldp_output.json
EOF

while read -r machine; do
  echo $machine
  scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $script $machine:/tmp/
  ssh -n -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $machine "chmod 700 $script; sudo $script; rm $script"
  scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $machine:'/tmp/lldp_output.json' $download_dir/$machine.json
done < machines.txt
exit 0
