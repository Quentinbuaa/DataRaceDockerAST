#!/bin/bash

DMEMLOG=mem.log
DCPULOG=cpu.log
DFNTLOG=mem_failcnt.log
DALLLOG=docker_all.log
PMEMLOG=pro_mem.log
PCPULOG=pro_cpu.log
PTXTLOG=pro_ctxt.log
PTXTLOG=pro_ctxt.log

STATLOGDIR=../statsLogs


check_and_clean(){
if test -f "$1";then
	rm ./$1
fi
}

clear_log_files(){
for file in $DMEMLOG $DCPULOG $DFNTLOG $DALLLOG $PMEMLOG $PCPULOG $PTXTLOG $PTXTLOG
do
	check_and_clean $file
done
}


get_docker_stats_file(){
# docker stat:
# $3 cpu%
# $7 mem%=used_memory/limited_memory	
docker stats --no-stream |awk 'END {print $3, $7}'>> $DALLLOG

}
get_docker_all_stats_info(){
curl -v --unix-socket /var/run/docker.sock \ http:localhost/containers/$CID/stats?stream=false	|jq '.'
}
get_docker_memory_stats_file() {
	#cat $MEM | awk '{print $1}' | tr '\n' '\t'|awk '{print $0}'>> mem.log 
	#$2 RSS
	#$8 pgpgin 
	#$9 pgpgout
	#$10 pgfault
	#$11 pgmajfault
	#$12 inactive_anon
	#$13 active_anon
	MEM=/sys/fs/cgroup/memory/docker/$CID/memory.stat
	cat $MEM | awk '{print $2}' | tr '\n' '\t'|awk '{print $2, $8, $9, $10, $11, $12, $13}'>> $DMEMLOG
}
get_docker_cpu_stats_file() {
	CPU=/sys/fs/cgroup/cpu/docker/$CID/cpu.stat
	#$2 nr_throttled number of throttled times
	#$2 throttled_time throttled time
	cat $CPU | awk '{print $2}' | tr '\n' '\t'|awk '{print $2, $3}'>> $DCPULOG
}
get_docker_failcnt_stats_file() {
	MEM_failcnt=/sys/fs/cgroup/memory/docker/$CID/memory.failcnt
	cat $MEM_failcnt >> $DFNTLOG
}
get_process_stats() {
	pid=$(ps -e |grep pbzip2 | awk '{print $1}') && cat /proc/$pid/stats >> stat.log
}

get_process_stats_file(){
	pidstat -r -h 1 1|grep pbzip2 | awk '{print $5, $6, $7, $8, $9}'>> $PMEMLOG
	pidstat -u -h 1 1|grep pbzip2 | awk '{print $5, $6, $7, $8, $9}'>> $PCPULOG
	pidstat -w -h 1 1|grep pbzip2 | awk '{print $5, $6}'>> $PTXTLOG
}

save_log_files(){
	if [ ! -d $STATLOGDIR ]
	then
		mkdir $STATLOGDIR
	fi
	mv ./$DMEMLOG $STATLOGDIR/mem_"$cpu_per"_"$mem_per".log
	mv ./$DFNTLOG $STATLOGDIR/mem_failcnt_"$cpu_per"_"$mem_per".log
	mv ./$DCPULOG $STATLOGDIR/cpu_"$cpu_per"_"$mem_per".log
	mv ./$DALLLOG $STATLOGDIR/docker_all_"$cpu_per"_"$mem_per".log
	mv ./$PMEMLOG $STATLOGDIR/pro_mem_"$cpu_per"_"$mem_per".log
	mv ./$PCPULOG $STATLOGDIR/pro_cpu_"$cpu_per"_"$mem_per".log
	mv ./$PTXTLOG $STATLOGDIR/pro_ctxt_"$cpu_per"_"$mem_per".log
}



monitor(){
	clear_log_files # clear all the log files
	export CID=$(docker ps -n -1 --no-trunc | awk 'NR>1 {print $1}')
	while true
	do
		cid_running=$(docker container inspect -f '{{.State.Running}}' $CID )
		if [ "$cid_running" == "true" ]
		then	
			echo "Monitoring a container every 5s."
			get_docker_memory_stats_file	
			get_docker_cpu_stats_file	
			get_docker_failcnt_stats_file	
			get_docker_stats_file
			get_process_stats_file
		else	
			echo "Container Stoped, and Monitoring Over."
			save_log_files
			break
		fi
		sleep 5
	done
}

for c in 0.1 0.15 0.2 0.25 0.3 0.35 0.4 0.45
do 
#	for m in 10M
	for m in 10M 12M 15M 20M 25M 30M
	do
		export cpu_per=$c  #This is for docker-compose file (.yml) to configure cpu maximum usage percent.
		export mem_per=$m  #This is for docker-compose file (.yml) to configure memory maximum limit rss.
		docker-compose config  # Update configure file
		sleep 2
		gnome-terminal -x docker-compose up  #start pbzip2 container
		sleep 2 
		monitor                             # start collect container and pbzip2 process running metrics (or stats info).
		echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
		echo ">>>>>>configure cpu=$c mem=$m finished >>>>>>>>>"
		echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
		sleep 2
############
## There is a bug here. We should pass the "./logs" information to docker-compose.yml file, and we should check if there exists a directory called "../logs"
###########

		ft_log=../logs/ft.log              #../logs is used as a shared volumne with docker pbzip2 container, and ft.log is a file to record the failing time of pbzip2.
		ft_prefix=hcft
		ft_log_name=../logs/"$ft_prefix"_"$cpu_per"_"$mem_per".log
		if test -f "$ft_log";then 
			mv $ft_log $ft_log_name
		fi
	done
done

