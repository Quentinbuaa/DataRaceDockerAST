
head_lines=open('head.txt', 'r').readlines()
data_lines=open('data.txt','r').readlines()
log=open('log.txt','w')
logs = []
for i in range(len(head_lines)):
	data_line = data_lines[i]
	data_items = data_line.split()
	data_items = [float(x) for x in data_items]
	mean = sum(data_items)/len(data_items)
	logs.append("{} {:.2f}\n".format(head_lines[i].rstrip(), mean))
log.writelines(logs)
log.close()
	
