#!/usr/bin/env python

import sys
import os
import fjd


if __name__ == '__main__':
    project = "default"
    if len(sys.argv) > 1:
        project = sys.argv[1]
    # first make sure the needed directories exists
    wdir = fjd.utils.ensure_wdir(project)
    fjd.utils.empty_queues(project)

    # now put 10 jobs in the queue
    for i in range(10):
        job = '''#!/bin/bash
python ajob.py value{} {}
'''.format(i, 'logfiles/job{}.dat'.format(i) )
        f = open('{}/jobqueue/job{i}'.format(wdir, i=i), 'w')
        f.write(job)
        f.close() 
        os.chmod('{}/jobqueue/job{i}'.format(wdir, i=i), 0777)
