#!/usr/bin/python
import os
import sys
from multiprocessing import cpu_count

from fjd.core_process import CoreProcess
from fjd.utils import ensure_wdir, empty_queues
from fjd import Recruiter, Dispatcher


class Main(CoreProcess):

    def __init__(self, exe, instances=1, parameters=[], project=None, curdir=''):
        if not exe or exe == '':
            print('[fjd] Please specify an executable command (--exe).')
            sys.exit(2)
        if instances > 1 and len(parameters) > 0:
            print('[fjd] Only one of --instances and --parameters can be set at a time.')
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
                        print j+1, param, cur_exe
                        if '${}'.format(j+1) in cur_exe:
                            print 'replacing'
                            cur_exe = cur_exe.replace('${}'.format(j+1), str(param))
                        else:
                            print 'not replacing'
                            ext_params.append(str(p))
                    print cur_exe
                    f.write('{exe} {params}'.format(exe=cur_exe, params=' '.join(ext_params)))
                os.chmod(job, 0777)
        else:
            for i in range(instances):
                job = '{}/jobqueue/job{}'.format(self.wdir, i)
                with open(job, 'w') as f:
                    f.write('#!/bin/bash\n')
                    f.write(exe)
                os.chmod(job, 0777)

        num_workers = min(instances, cpu_count())
        recruiter = Recruiter(num_workers=num_workers, project=project,
                              curdir=curdir)
        recruiter.hire()
        Dispatcher(project=project)

