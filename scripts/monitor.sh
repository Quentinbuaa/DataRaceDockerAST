for i in 1 2 3 4 5 6 
do
	old_rss=$(cat mem.log | awk 'END {print $2}')
	old_pgpgin=$(cat mem.log | awk 'END {print $8}')
	sleep 3
	new_rss=$( cat mem.log | awk 'END {print $2}')
	new_pgpgin=$( cat mem.log | awk 'END {print $8}')
	rss_rate=$((new_rss - old_rss ))
	pgpgin_rate=$(( new_pgpgin - old_pgpgin ))
	echo $rss_rate $pgpgin_rate
done
