#!/bin/bash
num_replica=10
num_max_rerun=5000
high_concurrency_level=100 # I think 100 is high
low_concurrency_level=3 # After testing, 3 is low. 
log_file=logs/ft.log

if test -f "$log_file"; then
	rm $log_file
fi
for replica in $(seq $num_replica)
do
	for i in $(seq $num_max_rerun)
	do
		./pbzip2 -k -f -p$high_concurrency_level ./test.tar # Think wether the 100 afect the result?
		exit=$?
		if [ $exit -ne 0 ]
		then
		#	if [ "$exit" == "139"  ]
		#	then 
			echo $i $exit >> $log_file
		#	fi
			printf "%d failure %d" $i $exit
			break
		fi
	done
	echo "Runing $replica (out of $num_replica)"
	sleep 2
done
