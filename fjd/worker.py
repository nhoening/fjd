#!/usr/bin/python

import os
import time
from ConfigParser import ConfigParser
import subprocess
from socket import gethostname

from fjd.core_process import CoreProcess
from fjd.utils import ensure_wdir


class Worker(CoreProcess):
    '''
    A worker process
    '''

    def __init__(self, interval=.1, project=None):
        if not project:
            project = 'default'
        self.wdir = ensure_wdir(project)
        self.start_up()

        # announce my presence
        self.id = self.mk_id()
        print('[fjd-worker] Started with ID {id}.'.format(id=self.id))
        subprocess.call('touch {wdir}/workerqueue/{id}.worker'\
                   .format(wdir=self.wdir, id=self.id), shell=True)

        # look for jobs
        while True:
            job = self.next_job_on_pod()
            if job:
                print('[fjd-worker] Worker {}: I found a job.'.format(self.id))
                # A job is a config file
                conf = ConfigParser() 
                conf.read('{}/jobpod/{}'.format(self.wdir, job))
                exe = conf.get('control', 'executable')
                exe_log = conf.get('control', 'logfile')
                # make log file and execute task
                cmd = 'touch {log}; {exe} {wdir}/jobpod/{job}; '\
                       .format(log=exe_log, exe=exe, wdir=self.wdir, job=job)
                subprocess.call(cmd, shell=True)
                print('[fjd-worker] Worker {}: Finished my job.'.format(self.id))
                # remove the job from pod (signaling it is done) + re-announce myself
                subprocess.call('rm {wdir}/jobpod/{job}; touch {wdir}/workerqueue/{id}.worker'\
                        .format(wdir=self.wdir, job=job, id=self.id), shell=True)
            time.sleep(interval)

    def mk_id(self):
        ms = time.time()
        return '{h}_{t}'.format(h=gethostname(), t=ms)

    def next_job_on_pod(self):
        my_jobs = [j for j in os.listdir('{}/jobpod'.format(self.wdir))\
                  if j.startswith(self.id)]
        if len(my_jobs) > 0:
            return my_jobs[0]
        else:
            return None

