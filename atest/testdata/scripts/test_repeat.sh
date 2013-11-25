#!/bin/sh

if [ -f counter.txt ]
then
    count=$(cat counter.txt)
    echo Current count is $count
    echo $((1+$count)) > counter.txt
else
    echo started counter;
    echo 1 > counter.txt;
fi
