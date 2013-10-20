#!/usr/bin/env python

import os
import time

from fjd import CoreProcess
from fjd import Recruiter


class Dispatcher(CoreProcess):
    '''
    Directory and File-based work dispatcher.
    Expects jobs to be put in directory `jobqueue` and workers to
    annouce themselves in directory `workerqueue`. Will then assign jobs 
    to workers by moving jobs to the `jobpod` directory. 
    '''

    def __init__(self, interval=5, wdir='~/.fjd', end_on_empty_queue=True):
        self.start_up(wdir=wdir)

        print("[FJD] Dispatcher started.")

        do_work = True
        while do_work:
            time.sleep(interval)
            jq = os.listdir('{}/jobqueue'.format(self.wdir))
            wq = os.listdir('{}/workerqueue'.format(self.wdir))
            if len(jq) > 0:
                print("[FJD] Found {} jobs and {} workers. Dispatching ..."\
                       .format(len(jq), len(wq)))
                for _ in range(min(len(jq), len(wq))):
                    worker = wq.pop()
                    job = jq.pop()
                    os.rename('{wdir}/jobqueue/{j}'.format(wdir=self.wdir, j=job),
                              '{wdir}/jobpod/{w}'.format(wdir=self.wdir, w=worker))
                    os.remove('{wdir}/workerqueue/{w}'.format(wdir=self.wdir, w=worker))
            elif end_on_empty_queue:
                print("[FJD] No (more) jobs to dispatch.")
                Recruiter().fire()
                do_work = False
            # TODO: maybe update a little stats file about work done so far
            #       and also who is currently busy? 
        
        self.wrap_up()


