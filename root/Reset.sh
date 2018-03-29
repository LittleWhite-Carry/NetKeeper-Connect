#!/bin/sh

uci set network.wan.ok="0"
uci commit
a=$(grep -c 'vwan' /etc/config/network)
for i in $(seq $a)
do
    if [ -z "$(ifconfig | grep "vwan$i")" ]
    then
        if [ $(uci get network.vwan$i.ok) -eq 1 ]
        then
            uci set network.vwan$i.ok="0"
            uci commit
            echo "vwan$i Reset"
            let n++
        fi
    fi
done
echo "Done"