#!/usr/bin/python

import os
import sys
import time
import io
try:
    import configparser
except ImportError:
    import ConfigParser as configparser  # for py2
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
                # Check if job file is a config file (ini-style).
                # If it is, get executable from there, call it and pass it the config file.
                # If it is not, run the job file as a script.

                # We read the file first and close it, so no stale handles will exists
                # in case ConfigParser exits
                with open('{}/jobpod/{}'.format(self.wdir, job), 'r') as jobfile:
                    jobtxt = jobfile.read()
                    if sys.version < '3':
                        jobtxt = unicode(jobtxt)
                ini_fp = io.StringIO(jobtxt)
                conf = configparser.RawConfigParser()
                try:
                    conf.readfp(ini_fp)  # this raises in case it is not an .ini file
                    exe = conf.get('fjd', 'executable')
                    cmd = 'nice -n {nice} {exe} {wdir}/jobpod/{job}; '\
                          .format(nice=9, exe=exe, wdir=self.wdir, job=job)
                    #except (configparser.MissingSectionHeaderError, configparser.NoSectionError):
                except (configparser.MissingSectionHeaderError):
                    cmd = 'nice -n {nice} {wdir}/jobpod/{job}'.format(nice=9, wdir=self.wdir, job=job)
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

