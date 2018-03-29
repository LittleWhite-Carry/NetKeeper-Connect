#!/bin/sh


for name in $*
do

    ifdown $name
    uci set network.$name.ok="0"
    uci commit

done

echo "Done"