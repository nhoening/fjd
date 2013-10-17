#!/usr/bin/python

import sys
import os
import time
from ConfigParser import ConfigParser
from subprocess import Popen

from fjd.core_process import CoreProcess


class Worker(CoreProcess):
    '''

    '''
    
    def __init__(self, interval=5, wdir='.fjd'):
        self.start_up(wdir=wdir)

        # announce my presence
        self.id = self.mk_id()
        self.wdir = wdir
        print('[FJD] Worker with ID {id} started.'.format(id=self.id))
        os.system('touch {wdir}/workerqueue/{id}.worker'.format(wdir=wdir,
                                                                id=self.id))

        while True:
            job = self.next_job_on_pod()
            if job:
                print('[FJD] Worker {}: I found a job.'.format(self.id))
                # A job is a config file
                conf = ConfigParser() 
                conf.read('{}/jobpod/{}'.format(wdir, job))
                exe = conf.get('control', 'executable') 
                log = conf.get('control', 'logfile') 
                # remove job from pod, execute task and re-announce myself
                cmd = 'touch {log}; {exe} jobpod/{job}; rm {wdir}/jobpod/{job}; '\
                      'touch {wdir}/workerqueue/{id}.worker'.format(exe=exe,
                                    job=job, wdir=wdir, log=log, id=self.id)
                Popen(cmd, shell=True).wait()
                print('[FJD] Worker {}: Finished my job.'.format(self.id))
            time.sleep(interval)

    def mk_id(self):
        host = os.uname()[1]
        ms = time.time()
        return '{h}_{t}'.format(h=host, t=ms)

    def next_job_on_pod(self):
        my_jobs = [j for j in os.listdir('{}/jobpod'.format(self.wdir))\
                  if j.startswith(self.id)]
        if len(my_jobs) > 0:
            return my_jobs[0]
        else:
            return None


if __name__ == '__main__':
    if len(sys.argv) == 1:
        Worker()
    else:
        Worker(wdir=sys.argv[1])
