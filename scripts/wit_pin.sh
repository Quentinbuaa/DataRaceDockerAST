#!/bin/bash

path=/home/kun/workspace/pbzip2-0.9.4
for i in $(seq 1000)
do
	/home/kun/Applications/pin/pin -t $path/inscount_tls.so -- $path/pbzip2 -k -f -p10 $path/test.tar
	exit=$?
	if [ $exit -ne 0 ]
	then
		printf "%d failure %d" $i $exit
		exit -1
	fi
done
	
