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
        self.cpu_usage = 0

class Action():
    def __init__(self, action):
        self.action = action
        self.metric = Metric()
        self.failure_time = 0

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
        fd = self._get_file(self.logsDir, 'ft', action)
        fts = []
        for line in fd.readlines():
            try:
                r = line.split()
                ft, exit_code = r[0], r[1]
                if exit_code == '139':
                    fts.append(int(ft))
                if exit_code == '137':
                    print("A run out of memory failre in file {}.".format(fd.name))
                if exit_code == '1':
                    print("A failure with 1 in file {}.".format(fd.name))
            except:
                print("Cannot parse a line in file {}.".format(fd.name))
                exit(-1)
        action.failure_time = sum(fts)/len(fts)

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
        action.metric.rss = sum(rss_l)/len(rss_l)  # I am calculating the average.
        action.metric.pgpgin_rate = self._get_average_rate(pgpgin_l, "pgpgin", fd.name) # since the pgpgin is accumulating, so I want to calculated the average rate.
        action.metric.pgpgout_rate = self._get_average_rate(pgpgout_l, "pgpgout", fd.name) # since the pgpgin is accumulating, so I want to calculated the average rate.
        action.metric.pgfault_rate = self._get_average_rate(pgfault_l, "pgfault", fd.name) # since the pgpgin is accumulating, so I want to calculated the average rate.
        action.metric.pgmajfault_rate = self._get_average_rate(pgmajfault_l, "pgmajfault", fd.name) # since the pgpgin is accumulating, so I want to calculated the average rate.
        action.metric.inactive_anon_rate = self._get_average_rate(pgmajfault_l, "pgmajfault", fd.name) # since the pgpgin is accumulating, so I want to calculated the average rate.

    def _get_average_rate(self, t_list, tag,  fd_name):
        dfs = []
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
        pattern = '^ft_(0\.[0-9]{1,2})_([0-9]{1,2})M\.log$'
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
    actions = [Action((0.1, 10))]
    for a in actions:
        parser.get_action_failure_time(a)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
