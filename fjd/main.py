#!/usr/bin/python
import os
import sys
from multiprocessing import cpu_count

from fjd.core_process import CoreProcess
from fjd.utils import ensure_wdir, empty_queues
from fjd import Recruiter, Dispatcher


class Main(CoreProcess):
    '''
    Translates --exe, --repeat and --parameters options into job files, then starts
    Recruiter and Dispatcher.
    '''
    def __init__(self, exe, repeat=1, parameters=[], project=None, num_workers=0,
                callback=None, curdir=''):
        if not exe or exe == '':
            print('[fjd] Please specify an executable command (--exe).')
            sys.exit(2)
        if repeat > 1 and len(parameters) > 0:
            print('[fjd] Only one of --repeat and --parameters can be set at a time.')
            sys.exit(2)
        empty_queues(project=project)
        self.wdir = ensure_wdir(project)
        if len(parameters) > 1:
            for i, p in enumerate(parameters):
                job = '{}/jobqueue/job{}'.format(self.wdir, i)
                with open(job, 'w') as f:
                    f.write('#!/bin/bash\n')
                    cur_exe = exe
                    ext_params = []
                    for j, param in enumerate(str(p).split('#')):
                        if '${}'.format(j+1) in cur_exe:
                            cur_exe = cur_exe.replace('${}'.format(j+1), str(param))
                        else:
                            ext_params.append(str(p))
                    f.write('{exe} {params}'.format(exe=cur_exe, params=' '.join(ext_params)))
                os.chmod(job, 0o777)
        else:
            for i in range(repeat):
                job = '{}/jobqueue/job{}'.format(self.wdir, i)
                with open(job, 'w') as f:
                    f.write('#!/bin/bash\n')
                    f.write(exe)
                os.chmod(job, 0o777)

        if num_workers == 0:
            num_workers = cpu_count() - 1
        num_workers = min(num_workers, cpu_count())
        recruiter = Recruiter(num_workers=num_workers, project=project,
                              curdir=curdir)
        recruiter.hire()
        Dispatcher(project=project, callback=callback)

