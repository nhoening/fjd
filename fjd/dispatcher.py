#!/usr/bin/env python

import sys
import os
import time
import signal
import types
import subprocess

from fjd import CoreProcess
from fjd import Recruiter
from fjd.utils import ensure_wdir


if sys.version < '3':
    input = raw_input


class Dispatcher(CoreProcess):
    '''
    Directory and File-based work dispatcher.
    Expects jobs to be put in directory `jobqueue` and workers to
    annouce themselves in directory `workerqueue`. Will then assign jobs 
    to workers by moving jobs to the `jobpod` directory. 
    '''

    def __init__(self, interval=.1, project=None, end_when_jobs_are_done=True,
                 callback=None, status_only=False):
        if not project:
            project = 'default'
        self.wdir = ensure_wdir(project)
        self.start_up()

        if not status_only:
            print('[fjd-dispatcher] Started on project "{}".'.format(project))

        def signal_handler(signal, frame):
            ''' gently exiting, e.g. when CTRL-C was pressed.  '''
            sys.stdout.write('\n[fjd-dispatcher] Received Exit signal. Exiting ...\n')
            print('[fjd-dispatcher] Should I fire all workers in project {}? [y|N]'\
                        .format(project))
            if input().lower() in ["y", "yes"]:
                Recruiter(project=project).fire()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

        do_work = True
        while do_work:
            time.sleep(interval)
            if status_only:  # just show info once, don't do anything else
                do_work = False
            jq = os.listdir('{}/jobqueue'.format(self.wdir))
            jp = os.listdir('{}/jobpod'.format(self.wdir))
            wq = os.listdir('{}/workerqueue'.format(self.wdir))
            self.sort_jobqueue(jq)
            num_workers = len(os.listdir('{}/screenrcs'.format(self.wdir)))
            if len(jq) > 0:  # more jobs waiting for workers
                sys.stdout.write("\r[fjd-dispatcher] {} job(s) waiting in the queue."\
                                 " Currently {} worker(s) out of {} are free ...                   "\
                       .format(len(jq), len(wq), num_workers))
                sys.stdout.flush()
                if not status_only:
                    for _ in range(min(len(jq), len(wq))):
                        worker = wq.pop()
                        job = jq.pop()
                        os.rename('{wdir}/jobqueue/{j}'.format(wdir=self.wdir, j=job),
                                '{wdir}/jobpod/{w}'.format(wdir=self.wdir, w=worker))
                        os.remove('{wdir}/workerqueue/{w}'.format(wdir=self.wdir, w=worker))
            elif len(jp) > 0:  # some jobs are still running
                sys.stdout.write("\r[fjd-dispatcher] Job queue is empty. Waiting for remaining {} job(s) to finish ...                  ".format(len(jp)))
                sys.stdout.flush()
            else:  # all jobs are done
                sys.stdout.write("\r[fjd-dispatcher] Job queue is empty and all jobs have finished.                                     ")
                sys.stdout.flush()
                if end_when_jobs_are_done:
                    sys.stdout.write("\n")
                    Recruiter(project=project).fire()
                    do_work = False
                    if callback:
                        if isinstance(callback, types.FunctionType):
                            callback()
                        elif isinstance(callback, str):
                            subprocess.call(callback, shell=True)
                        else:
                            print('[fjd-dispatcher] Cannot use callback function, as it is neither function nor string, but {}'.format(type(callback)))
            if status_only:
                print('')

        self.wrap_up()

    def sort_jobqueue(self, jobqueue):
        '''
        Sort jobs - overwrite to enable dynamic queueing.
        Only an idea as of now, see issue #13
        '''
        pass
