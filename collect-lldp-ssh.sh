#!/usr/bin/env bash

download_dir='/tmp/lldp'

mkdir -p $download_dir

while read -r machine; do
  echo $machine
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "lldpcli show neighbors details -f json > lldp_output.json"
  scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $machine:'~/lldp_output.*' $download_dir/$machine.json
done < $1
