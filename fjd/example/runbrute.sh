#!/usr/bin/env python

'''
This is a simple example of using fjd to run >600K jobs on a PBS
computation cluster.
I make parameter configurations from four shuffled lists and let one job run 1000 parameter configurations (otherwise, the job queue becomes too large and it takes too long for fjd to regularly inspect it).
'''

import sys
import itertools
import numpy as np
import random
from subprocess import call
from fjd import Dispatcher
from fjd.utils import ensure_wdir, empty_queues

# clean up
call('rm pbsjobs/job*', shell=True)
call('rm brute.log; touch brute.log', shell=True)
ensure_wdir(project='brute')
empty_queues(project='brute')

# start 80 workers on 10 PBS nodes (8 on each)
for node in xrange(1, 11, 1):
    pbsjob = '''# Shell for the job:
#PBS -S /bin/bash
# request 1 node, 8 cores
#PBS -lnodes=1:cores8
# job requires at most n hours wallclock time
#PBS -lwalltime=16:00:00

cd /home/nicolas/brute
fjd-recruiter --project brute hire 8
python -c "import time; time.sleep(16*60*60)"  # keep PBS job alive
'''
    with open("pbsjobs/job{}".format(node), 'w') as f:
        f.write(pbsjob)
    call('qsub pbsjobs/job{}'.format(node), shell=True)


# fill jobqueue
cpus = 80
random.seed(1234)  # seed used for shuffling
jobs_per_batch = 1000  # so the job list isn't too long for the dispatcher

space0 = np.linspace(0.01, .75, 30)
random.shuffle(space0)
space1 = np.linspace(0.01, 0.6, 30)
random.shuffle(space1)
space2 = np.linspace(0.01, 5, 50)
random.shuffle(space2)
space_mp = np.linspace(0.01, .75, 15)
random.shuffle(space_mp)

jobs = itertools.product(space0, space1, space2, space_mp)

batchid = 0
f = open('dummy', 'w')
for jobid, job in enumerate(jobs):
    if jobid % jobs_per_batch == 0 or batchid == 0:
        f.close()
        f = open("/home/nicolas/.fjd/brute/jobqueue/batch-{}".format(batchid), 'w')
        f.write('#!/bin/bash\n')
        f.write('cd /home/nicolas/brute\n')
        batchid += 1
    f.write('brute.py {x0} {x1} {x2} {mp}\n'.format(x0=job[0], x1=job[1], x2=job[2], mp=job[3]))

Dispatcher(project='brute')

