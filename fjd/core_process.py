import os
import os.path as osp


class CoreProcess(object):
    '''
    Superclass of classes that represent a longer-running process, i.e.
    Worker and Dispatcher.

    We could do things here that are needed for all processes on a cluster 
    core, e.g. notify cluster management that we exist or that we stopped.
    '''

    def start_up(self, wdir='~/.fjd'):
        ''' expand working diretory path and create needed directories. '''
        self.wdir = osp.expanduser(wdir)
        if not osp.exists(self.wdir):
            os.mkdir(self.wdir)
        for d in ('jobqueue', 'jobpod', 'workerqueue'):
            if not osp.exists('{}/{}'.format(self.wdir, d)):
                os.mkdir('{}/{}'.format(self.wdir, d))

    def wrap_up(self):
        pass
