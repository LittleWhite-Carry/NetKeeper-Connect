#!/bin/sh

#start pppoe-server
if [ -n "$(ps | grep pppoe-server | grep -v grep)" ]
then
    killall pppoe-server
fi
pppoe-server -k -I br-lan

ifup wan

uci set network.wan.ok="0"
uci commit

a=$(grep -c 'vwan' /etc/config/network)

for i in $(seq 1 $a)
do

    uci set network.vwan$i.ok="0"
    ifdown vwan$i
    uci commit

done
