#!/usr/bin/env python

import os
import os.path as osp

if __name__ == '__main__':

    wdir = osp.expanduser('~/.fjd')
    for d in ('logfiles', wdir, '{wdir}/jobqueue'.format(wdir=wdir)):
        if not os.path.exists(d):
            os.mkdir(d)

    for i in range(10):
        jobconf = '''[control]
executable: python test/ajob.py
logfile: logfiles/job{i}.dat 

[params]
param1:value{i}'''.format(i=i)    
        f = open('{wdir}/jobqueue/{i}.conf'.format(wdir=wdir, i=i), 'w')
        f.write(jobconf)
        f.close() 
