#!/usr/bin/python

if __name__ == '__main__':
    for i in range(10):
        jobconf = '''[meta]
executable: python test/ajob.py
logfile:data/job{i}.dat 

[params]
param1:value{i}'''.format(i=i)    
        f = open('jobqueue/{i}.conf'.format(i=i), 'w')
        f.write(jobconf)
        f.close() 
