#!/usr/local/bin/python3.9

import os
import re


class Metric():
    def __init__(self):
        self.rss = 0
        self.pgpgin_rate =0
        self.pgpgout_rate =0
        self.pgfault_rate =0
        self.pgmajfault_rate =0
        self.active_anon_rate =0
        self.inactive_anon_rate =0
        self.nr_throttled=0
        self.throttled_time=0
        self.usr_cpu_usage = 0
        self.sys_cpu_usage = 0
        self.wait_cpu = 0
        self.total_cpu = 0
        self.pro_minflt = 0
        self.pro_majflt =0
        self.pro_vsz =0
        self.pro_rss =0
        self.pro_mem =0
        self.pro_cswch=0
        self.pro_nvcswch=0
        self.docker_cpu_usage = 0
        self.docker_mem_usage = 0

    def toPrintKeys(self):
        attrs = vars(self)
        return '\t'.join([k for k in attrs.keys()])
    def toPrintValues(self):
        attrs = vars(self)
        return '\t'.join(["{:.2f}".format(attrs[k]) for k in attrs.keys()])

    def toPrint(self):
        docker_info ="{0:.2f}\t{1:.2f}".format(self.docker_cpu_usage, self.docker_mem_usage)
        pro_cpu_info ="{0:.2f}\t{1:.2f}\t{2:.2f}\t{3:.2f}".format(self.usr_cpu_usage, self.sys_cpu_usage, self.wait_cpu, self.total_cpu)
        pro_mem_info ="{0:.2f}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}".format(self.pro_minflt, self.pro_majflt, self.pro_vsz, self.pro_rss, self.pro_mem)
        pro_ctxt_info ="{0:.2f}\t{1:.2f}".format(self.pro_cswch, self.pro_nvcswch)
        cpu_info = "{0:.2f}\t{1:.2f}".format(self.nr_throttled, self.throttled_time)
        mem_info ="{0:.2f}\t{1:.2f}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}".format(
                                        self.rss, self.pgpgin_rate, self.pgpgout_rate,
                                          self.pgfault_rate, self.pgmajfault_rate,
                                          self.inactive_anon_rate, self.active_anon_rate)
        return "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(mem_info, cpu_info, pro_cpu_info, pro_mem_info, pro_ctxt_info, docker_info)


class Action():
    def __init__(self, action):
        self.action = action
        self.metric = Metric()
        self.failure_time = 0

    def toPrintKeys(self):
        return '\t'.join(['cpu_limit', 'mem_limit', ])+'\t'+self.metric.toPrintKeys()+'\t failure_time'

    def toPrintValues(self):
        action_name = "{}\t{}".format(self.action[0], self.action[1])
        return "{0}\t{1}\t{2:.2f}".format(action_name, self.metric.toPrintValues(), self.failure_time)

class myParser():
    def __init__(self):
        self.logsDir='../logs'
        self.stats_logs_dir='../statsLogs'
        self.repeat_time = 5000
        self.replica_time = 10

    def _get_file(self, dir, prefix, action):
        fd = open("{}/{}_{}_{}M.log".format(dir, prefix,action.action[0], action.action[1]), 'r')
        return fd

    def get_action_failure_time(self, action):
        fd = self._get_file(self.logsDir, 'newft', action)
        fts = []
        flag = False
        for line in fd.readlines():
            try:
                r = line.split()
                ft, exit_code = r[0], r[1]
                if exit_code == '139':
                    fts.append(int(ft))
                if exit_code == '137':
                    flag = True
                    print("A run out of memory failre in file {}.".format(fd.name))
                if exit_code == '1':
                    flag = True
                    print("A failure with 1 in file {}.".format(fd.name))
            except:
                print("Cannot parse a line in file {}.".format(fd.name))
                exit(-1)
        if flag == False and len(fts) < self.replica_time:
            fts = fts + [self.repeat_time]* (self.replica_time - len(fts))
        action.failure_time = sum(fts)/len(fts)

    def get_action_pro_mem_metrics(self, action):
        fd = self._get_file(self.stats_logs_dir, 'pro_mem', action)
        pro_minflt_l = []
        pro_majflt_l = []
        pro_vsz_l = []
        pro_rss_l = []
        pro_mem_l = []
        for line in fd.readlines():
            r = line.split()
            try:
                pro_minflt_l.append(float(r[0]))
                pro_majflt_l.append(float(r[1]))
                pro_vsz_l.append(int(r[2]))
                pro_rss_l.append(int(r[3]))
                pro_mem_l.append(float(r[4]))
            except:
                print("cannot parse a line in file {}.".format(fd.name))
                exit(-1)
        action.metric.pro_minflt = self._get_max(pro_minflt_l,'pro minflt', fd.name)
        action.metric.pro_majflt = self._get_max(pro_majflt_l,'pro majflt', fd.name)
        action.metric.pro_vsz = self._get_max(pro_vsz_l,'pro vsz', fd.name)
        action.metric.pro_rss = self._get_max(pro_rss_l,'pro rss', fd.name)
        action.metric.pro_mem = self._get_max(pro_mem_l,'pro mem', fd.name)

    def get_action_pro_ctxt_metrics(self, action):
        fd = self._get_file(self.stats_logs_dir, 'pro_ctxt', action)
        pro_cswch_l = []
        pro_nvcswch_l = []
        for line in fd.readlines():
            r = line.split()
            try:
                pro_cswch_l.append(float(r[0]))
                pro_nvcswch_l.append(float(r[1]))
            except:
                print("cannot parse a line in file {}.".format(fd.name))
                exit(-1)
        action.metric.pro_cswch = self._get_max(pro_cswch_l, 'pro cswch', fd.name)
        action.metric.pro_nvcswch = self._get_max(pro_nvcswch_l, 'pro nvcswch', fd.name)

    def get_action_pro_cpu_metrics(self, action):
        fd = self._get_file(self.stats_logs_dir, 'pro_cpu', action)
        usr_cpu_usage_l = []
        sys_cpu_usage_l = []
        wait_cpu_l = []
        total_cpu_l = []
        for line in fd.readlines():
            r = line.split()
            try:
                usr_cpu_usage_l.append(float(r[0]))
                sys_cpu_usage_l.append(float(r[1]))
                wait_cpu_l.append(float(r[3]))
                total_cpu_l.append(float(r[4]))
            except:
                print("cannot parse a line in file {}.".format(fd.name))
                exit(-1)
        action.metric.usr_cpu_usage = self._get_max(usr_cpu_usage_l, 'usr_cpu', fd.name)
        action.metric.sys_cpu_usage = self._get_max(sys_cpu_usage_l, 'sys_cpu', fd.name)
        action.metric.wait_cpu = self._get_max(wait_cpu_l, 'wait_cpu', fd.name)
        action.metric.total_cpu = self._get_max(total_cpu_l, 'total_cpu', fd.name)

    def _get_max(self, t_list, tag, fd_name):
        try:
            return max(t_list)
        except:
            print("There is no sufficient data when parse {} in file {}".format(tag, fd_name))
            exit(-1)

    def get_action_cpu_metrics(self, action):
        fd = self._get_file(self.stats_logs_dir, 'cpu', action)
        nr_throttled_l = []
        throttled_time_l = []
        for line in fd.readlines():
            r = line.split()
            try:
                nr_throttled_l.append(int(r[0]))
                throttled_time_l.append(int(r[1]))
            except:
                print("Fail to parse memory metrics in log file {}".format(fd.name))
                exit(-1)
        action.metric.nr_throttled = self._get_average_rate(nr_throttled_l, "nr_throttled", fd.name) # since the nr_throttled is accumulating, so I want to calculated the average rate.
        action.metric.throttled_time = self._get_average_rate(throttled_time_l, "throttled_time", fd.name) # since the throttled_time is accumulating, so I want to calculated the average rate.

    def get_action_docker_all_metrics(self, action):
        fd = self._get_file(self.stats_logs_dir, 'docker_all', action)
        docker_cpu_usage_l = []
        docker_mem_usage_l = []
        pattern = '^([0-9]{1,2}\.[0-9]{1,2})%\s([0-9]{1,2}\.[0-9]{1,2})%'
        for line in fd.readlines():
            try:
                r = re.match(pattern, line)
                if r:
                    docker_cpu_usage_l.append(float(r[1]))
                    docker_mem_usage_l.append(float(r[2]))
            except:
                print("Fail to parse memory metrics in log file {}".format(fd.name))
                exit(-1)
        action.metric.docker_cpu_usage = self._get_max(docker_cpu_usage_l, 'docker cpu', fd.name)
        action.metric.docker_mem_usage = self._get_max(docker_mem_usage_l, 'docker mem', fd.name)


    def get_action_mem_metrics(self, action):
        fd = self._get_file(self.stats_logs_dir, 'mem', action)
        rss_l = []
        pgpgin_l=[]
        pgpgout_l = []
        pgfault_l = []
        pgmajfault_l = []
        inactive_anon_l = []
        active_anon_l = []
        for line in fd.readlines():
            r = line.split()
            try:
                rss_l.append(int(r[0]))
                pgpgin_l.append( int( r[1] ))
                pgpgout_l.append( int( r[2] ))
                pgfault_l.append( int( r[3] ))
                pgmajfault_l.append( int( r[4] ))
                inactive_anon_l.append( int( r[5] ))
                active_anon_l.append( int( r[6] ))
            except:
                print("Fail to parse memory metrics in log file {}".format(fd.name))
                exit(-1)
        action.metric.rss = self._get_average(rss_l, "rss", fd.name)  # I am calculating the average.
        action.metric.pgpgin_rate = self._get_average_rate(pgpgin_l, "pgpgin", fd.name) # since the pgpgin is accumulating, so I want to calculated the average rate.
        action.metric.pgpgout_rate = self._get_average_rate(pgpgout_l, "pgpgout", fd.name) # since the pgpgout is accumulating, so I want to calculated the average rate.
        action.metric.pgfault_rate = self._get_average_rate(pgfault_l, "pgfault", fd.name) # since the pgfault is accumulating, so I want to calculated the average rate.
        action.metric.pgmajfault_rate = self._get_average_rate(pgmajfault_l, "pgmajfault", fd.name) # since the pgmajfault is accumulating, so I want to calculated the average rate.
        action.metric.inactive_anon_rate = self._get_average(inactive_anon_l, "inactive_anon", fd.name) # since the inactive_anon is accumulating, so I want to calculated the average.
        action.metric.active_anon_rate = self._get_average(active_anon_l, "active_anon", fd.name) # since the active_anon is accumulating, so I want to calculated the average.

    def _get_average(self, t_list, tag, fd_name):
        try:
            return sum(t_list) /len(t_list)
        except:
            print("There is no sufficient data when parse {} in file {}".format(tag, fd_name))
            exit(-1)

    def _get_average_rate(self, t_list, tag,  fd_name):
        dfs = []
        if len(t_list) ==0:
            print("There is no sufficient data when parse {} in file {}".format(tag, fd_name))
            exit(-1)
        if len(t_list)==1:
            return t_list[0]
        for i in range(len(t_list) - 1):
            df = t_list[i+1] - t_list[i]
            if df <0:
                print("There is a minus value when parse {} in file {}".format(tag, fd_name))
                exit(-1)
            else:
                dfs.append(df)
        return sum(dfs)/len(dfs)

    def get_actions(self):
        pattern = '^newft_(0\.[0-9]{1,2})_([0-9]{1,2})M\.log$'
        actions = []
        for file in os.listdir(self.logsDir):
            result = re.match(pattern, file)
            if result:
                action = (result[1], result[2])
                actions.append(Action(action))
        return actions


if __name__ == '__main__':
    parser = myParser()
    actions = parser.get_actions()
    #actions = [Action((0.1, 10))]
    print(actions[0].toPrintKeys())
    for a in actions:
        parser.get_action_failure_time(a)
        parser.get_action_mem_metrics(a)
        parser.get_action_cpu_metrics(a)
        parser.get_action_pro_cpu_metrics(a)
        parser.get_action_pro_mem_metrics(a)
        parser.get_action_pro_ctxt_metrics(a)
        parser.get_action_docker_all_metrics(a)
        print(a.toPrintValues())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
