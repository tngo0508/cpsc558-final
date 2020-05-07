#!/bin/bash

ryu-manager QSwitch.py --verbose --log-file=ryu.log &
sudo mn --controller=remote,ip=192.168.1.187 --custom mininet_topo_test.py --topo mytopo --switch ovs --mac