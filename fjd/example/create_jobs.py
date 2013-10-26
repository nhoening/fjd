#!/usr/bin/env python

import sys
import os

if __name__ == '__main__':
    # first make sure the ~/.fjd/<project>/jobqueue directory exists
    fjd_dir = os.path.expanduser('~/.fjd')
    project = "default"
    if len(sys.argv) > 1:
        project = sys.argv[1]
    for d in ('logfiles', fjd_dir, '{}/{}'.format(fjd_dir, project),
              '{}/{}/jobqueue'.format(fjd_dir, project)):
        if not os.path.exists(d):
            os.mkdir(d)

    # now put 10 jobs in the queue
    for i in range(10):
        jobconf = '''[control]
executable: python ajob.py
logfile: logfiles/job{i}.dat 

[params]
param1:value{i}'''.format(i=i)
        f = open('{}/{}/jobqueue/{i}.conf'.format(fjd_dir, project, i=i), 'w')
        f.write(jobconf)
        f.close() 
