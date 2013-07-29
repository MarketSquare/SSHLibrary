#!/bin/sh

if [ "$1" != "" ]; then
    echo $1
else
    echo This is stdout
    echo This is stderr 1>&2
fi
