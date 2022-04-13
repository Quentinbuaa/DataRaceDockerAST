get_head(){
ls | awk '{print $1}'|awk '$0 ~ /^ft/ {print $0}'|awk -F '_' '{print $2, $3}'|awk '{print $1, $2}'|sed -e 's/.log//g'>head.txt
}
get_data(){
ft_files=$(ls |awk '$0~/^ft/ {print $0}')
for ft_file in $ft_files
do
	cat $ft_file |awk '$2~/139/ {print $1}'|tr '\n' '\t'|xargs echo|tee -a data.txt
done
}
merge(){
python merge.py
}
get_head
get_data
merge 
cat log.txt
