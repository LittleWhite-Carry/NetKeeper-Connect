#!/bin/sh

for name in $*
do

    if [ "$(ifconfig | grep "$name")" ]
    then
        echo "$name Connect"
    else
        echo "$name Down"
    fi

done

echo "Done"