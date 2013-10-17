#!/usr/bin/env python

import os

if __name__ == '__main__':

    for d in ('logfiles', '.fjd', '.fjd/jobqueue'):
        if not os.path.exists(d):
            os.mkdir(d)

    for i in range(10):
        jobconf = '''[control]
executable: python test/ajob.py
logfile: logfiles/job{i}.dat 

[params]
param1:value{i}'''.format(i=i)    
        f = open('.fjd/jobqueue/{i}.conf'.format(i=i), 'w')
        f.write(jobconf)
        f.close() 
