#!/usr/bin/env python

import sys
import os

import fjd


if __name__ == '__main__':
    project = "default"
    if len(sys.argv) > 1:
        project = sys.argv[1]
    # first make sure the needed directories exists
    wdir = fjd.utils.ensure_wdir(project)
    fjd.utils.empty_queues(project)
    if not os.path.exists('logfiles'):
        os.mkdir('logfiles')

    # now put 10 jobs in the queue
    for i in range(10):
        jobconf = '''[control]
executable: python ajob.py
logfile: logfiles/job{i}.dat 

[params]
param1:value{i}'''.format(i=i)
        f = open('{}/jobqueue/{i}.conf'.format(wdir, i=i), 'w')
        f.write(jobconf)
        f.close() 
