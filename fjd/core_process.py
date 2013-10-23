
class CoreProcess(object):
    '''
    Superclass of classes that represent a longer-running process, i.e.
    Worker and Dispatcher.

    Not sure if needed - we could do things here that are needed for all
    processes on a cluster core, e.g. notify cluster management that we exist 
    or that we stopped.
    '''

    def start_up(self):
        pass

    def wrap_up(self):
        pass
