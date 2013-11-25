#!/bin/sh

echo -n "Give your name?" 
read  NAME
if [ "$NAME" = "Error" ]; then 
    echo This is Error 1>&2;
fi
echo Hello $NAME
