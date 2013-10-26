#!/usr/bin/env python

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

    def __init__(self, interval=5, project=None, end_on_empty_queue=True):
        if not project:
            project = 'default'
        self.wdir = ensure_wdir(project)
        self.start_up()

        print('[fjd-dispatcher] Started on project "{}"'.format(project))

        do_work = True
        while do_work:
            time.sleep(interval)
            jq = os.listdir('{}/jobqueue'.format(self.wdir))
            wq = os.listdir('{}/workerqueue'.format(self.wdir))
            if len(jq) > 0:
                print("[fjd-dispatcher] Found {} job(s) and {} worker(s)..."\
                       .format(len(jq), len(wq)))
                for _ in range(min(len(jq), len(wq))):
                    worker = wq.pop()
                    job = jq.pop()
                    os.rename('{wdir}/jobqueue/{j}'.format(wdir=self.wdir, j=job),
                              '{wdir}/jobpod/{w}'.format(wdir=self.wdir, w=worker))
                    os.remove('{wdir}/workerqueue/{w}'.format(wdir=self.wdir, w=worker))
            elif end_on_empty_queue:
                print("[fjd-dispatcher] No (more) jobs.")
                Recruiter(project=project).fire()
                do_work = False
            # TODO: maybe update a little stats file about work done so far
            #       and also who is currently busy? 
        
        self.wrap_up()


