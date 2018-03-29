#!/bin/sh

cat /dev/null > /tmp/pppoe.log


for name in $*
do
    while :
    do
    
        if [ "$(grep 'user=' /tmp/pppoe.log | grep 'rcvd' | tail -n 1 | cut -d \" -f 5)" == "]" ]
        then
            username=$(grep 'user=' /tmp/pppoe.log | grep 'rcvd' | tail -n 1 | cut -d \" -f 2)
        fi
        
        if [ "$username" != "$username_old" ]
        then
            let n++
            ifdown $name
            uci set network.$name.username="$username"
            uci set network.$name.password="$(grep 'user=' /tmp/pppoe.log | grep 'rcvd' | tail -n 1 | cut -d \" -f 4)"
            uci commit
            username_old="$username"
            echo "$name"
            break
        fi

        sleep 1

    done

done

for name in $*
do

    ifup $name

done

uci set network.wan.ok="0"
uci commit

echo "Done"