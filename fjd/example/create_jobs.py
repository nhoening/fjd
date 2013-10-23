#!/usr/bin/env python

import os

if __name__ == '__main__':
    fjd_dir = os.path.expanduser('~/.fjd')
    for d in ('logfiles', fjd_dir, '{}/default'.format(fjd_dir),
              '{}/default/jobqueue'.format(fjd_dir)):
        if not os.path.exists(d):
            os.mkdir(d)

    for i in range(10):
        jobconf = '''[control]
executable: python ajob.py
logfile: logfiles/job{i}.dat 

[params]
param1:value{i}'''.format(i=i)    
        f = open('{}/default/jobqueue/{i}.conf'.format(fjd_dir, i=i), 'w')
        f.write(jobconf)
        f.close() 
