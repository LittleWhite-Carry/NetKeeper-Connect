#!/bin/sh

if [ $(uci get network.wan.ok) -eq 0 ]
then
    uci set network.wan.ok="1"
    uci commit
    a=$(grep -c 'vwan' /etc/config/network)
    if [ $a -eq 0 ]
    then
        echo "No VWAN"
    else
        n=0
        for i in `seq $a`
        do
            if [ -z "$(ifconfig | grep "vwan$i")" ]
            then
                if [ $(uci get network.vwan$i.ok) -eq 0 ]
                then
                    uci set network.vwan$i.ok="1"
                    uci commit
                    echo "vwan$i"
                    ifdown vwan$i
                    let n++
                fi
            fi
            if [ $n -eq $1 ]
            then
                break
            fi
        done
    fi
    echo "Done"
else
    echo "Wan is using"
fi