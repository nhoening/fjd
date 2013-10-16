#!/usr/bin/env python

import os
import time

from fjd.core_process import CoreProcess


class Dispatcher(CoreProcess):
    '''
    Directory and File-based work dispatcher.
    Expects jobs to be put in directory `jobqueue` and workers to
    annouce themselves in directory `workerqueue`. Will then assign jobs 
    to workers by moving jobs to the `jobpod` directory. 
    '''

    def __init__(self, interval=5):
        self.start_up()

        print("[FJD] Dispatcher started.")

        # prepare and clean
        for d in ('jobqueue', 'workerqueue', 'jobpod'):
            if not os.path.exists(d):
                os.mkdir(d)
            for f in os.listdir(d):
                os.remove('{d}/{f}'.format(d=d, f=f))

        do_work = True
        while do_work:
            jq = os.listdir('jobqueue')
            wq = os.listdir('workerqueue')
            if len(jq) > 0:
                print "Found some jobs to dispatch"
                # TODO: if there are more jobs than workers, assign all jobs already
                for _ in range(min(len(jq), len(wq))):
                    worker = wq.pop()
                    job = jq.pop()
                    os.rename('jobqueue/{j}'.format(j=job),
                              'jobpod/{w}'.format(w=worker))
                    os.remove('workerqueue/{w}'.format(w=worker))
            time.sleep(interval)
            do_work = not self.are_we_done()
            # TODO: maybe update a little stats file about work done so far
            #       and also who is currently busy? 
        
        self.wrap_up()

if __name__ == '__main__':
    Dispatcher()
