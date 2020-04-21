#!/usr/bin/env bash

download_dir='/tmp/lldp'

mkdir -p $download_dir

for machine in {0..12}; do
  host=$( juju ssh $machine hostname | tr -d '\r'  )
  juju scp $machine:'~/lldp_output.*' $download_dir/$host.json
done
