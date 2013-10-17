import os
import os.path as osp


class CoreProcess(object):
    '''
    We could do things here that are needed for all processes on a cluster 
    core, e.g. notify cluster management that we exist or that we stopped.
    '''

    def start_up(self, wdir='.fjd'):
        if not osp.exists(wdir):
            os.mkdir(wdir)
        for d in ('jobqueue', 'jobpod', 'workerqueue'):
            if not osp.exists('{}/{}'.format(wdir, d)):
                os.mkdir('{}/{}'.format(wdir, d))

    def wrap_up(self):
        pass
