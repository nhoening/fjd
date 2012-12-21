#!/usr/bin/python

import os
import time
from ConfigParser import ConfigParser
from subprocess import Popen

from core_process import CoreProcess


class Worker(CoreProcess):
    '''

    '''
    
    def __init__(self, interval=5):
        self.start_up()

        # announce my presence
        self.id = self.mk_id()
        print('[Worker with ID {id} started.]'.format(id=self.id))
        os.system('touch workerqueue/{id}.worker'.format(id=self.id))

        do_work = True
        while do_work:
            job = self.next_job_on_pod()
            if job:
                print('I found a job ({})'.format(self.id))
                # A job is a config file
                conf = ConfigParser() 
                conf.read('jobpod/{}'.format(job))
                exe = conf.get('control', 'executable') 
                log = conf.get('control', 'logfile') 
                # remove job from pod, execute task and re-announce myself
                cmd = 'touch {log}; {exe} jobpod/{job}; rm jobpod/{job}; '\
                      'touch workerqueue/{id}.worker'.format(exe=exe, job=job,
                                                          log=log, id=self.id)
                Popen(cmd, shell=True).wait()
                print('Did my job ({})'.format(self.id))
            time.sleep(interval)
            do_work = not self.are_we_done()

    def mk_id(self):
        host = os.uname()[1]
        ms = time.time()
        return '{h}_{t}'.format(h=host, t=ms)

    def next_job_on_pod(self):
        my_jobs = [j for j in os.listdir('jobpod') if j.startswith(self.id)]
        if len(my_jobs) > 0:
            return my_jobs[0]
        else:
            return None

if __name__ == '__main__':
    Worker()
