#!/usr/bin/python
import os
import sys
from multiprocessing import cpu_count

from fjd.core_process import CoreProcess
from fjd.utils import ensure_wdir, empty_queues
from fjd import Recruiter, Dispatcher


class Main(CoreProcess):

    def __init__(self, exe, instances=1, parameters=[], project=None, curdir):
        if not exe or exe == '':
            print('[fjd] Please specify an executable command.')
            sys.exit(2)
        if instances > 1 and len(parameters) > 0:
            print('[fjd] Only one of instances and parameters can be set at a time.')
            sys.exit(2)
        empty_queues(project=project)
        self.wdir = ensure_wdir(project)
        if len(parameters) > 1:
            for i, p in enumerate(parameters):
                with open('{}/jobqueue/job{}'.format(self.wdir, i)) as f:
                    f.write('{} {}'.format(exe, ' '.join(parameters)))
        else:
            for i, p in range(instances):
                with open('{}/jobqueue/job{}'.format(self.wdir, i)) as f:
                    f.write(exe)
            
        recruiter = Recruiter(num_workers=max(1, cpu_count() - 1), project=project,
                              curdir=curdir)
        recruiter.hire()
        Dispatcher(project=project, interval=args.interval)

