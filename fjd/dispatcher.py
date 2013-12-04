#!/usr/bin/env python

import sys
import os
import time

from fjd import CoreProcess
from fjd import Recruiter
from fjd.utils import ensure_wdir


class Dispatcher(CoreProcess):
    '''
    Directory and File-based work dispatcher.
    Expects jobs to be put in directory `jobqueue` and workers to
    annouce themselves in directory `workerqueue`. Will then assign jobs 
    to workers by moving jobs to the `jobpod` directory. 
    '''

    def __init__(self, interval=.1, project=None, end_on_empty_queue=True):
        if not project:
            project = 'default'
        self.wdir = ensure_wdir(project)
        self.start_up()

        print('[fjd-dispatcher] Started on project "{}"'.format(project))

        do_work = True
        while do_work:
            time.sleep(interval)
            jq = os.listdir('{}/jobqueue'.format(self.wdir))
            jp = os.listdir('{}/jobpod'.format(self.wdir))
            wq = os.listdir('{}/workerqueue'.format(self.wdir))
            if len(jq) > 0:  # more jobs waiting for workers
                sys.stdout.write("\r[fjd-dispatcher] {} job(s) waiting in the queue. Currently {} worker(s) are free...  "\
                       .format(len(jq), len(wq)))
                sys.stdout.flush()
                for _ in range(min(len(jq), len(wq))):
                    worker = wq.pop()
                    job = jq.pop()
                    os.rename('{wdir}/jobqueue/{j}'.format(wdir=self.wdir, j=job),
                              '{wdir}/jobpod/{w}'.format(wdir=self.wdir, w=worker))
                    os.remove('{wdir}/workerqueue/{w}'.format(wdir=self.wdir, w=worker))
            elif len(jp) > 0:  # some jobs are still running
                sys.stdout.write("\r[fjd-dispatcher] Queue is empty. Waiting for remaining {} job(s) to finish ...        ".format(len(jp)))
                sys.stdout.flush()
            else:  # all jobs are done
                sys.stdout.write("\r[fjd-dispatcher] Queue is empty and all jobs have finished.                          ")
                sys.stdout.flush()
                if end_on_empty_queue:
                    Recruiter(project=project).fire()
                    do_work = False
        self.wrap_up()

