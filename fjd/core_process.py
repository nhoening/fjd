

class CoreProcess(object):
    '''
    We could do things here that are needed for all processes on a cluster 
    core, e.g. notify cluster management that we exist or that we stopped.
    '''

    def start_up(self):
        pass

    def are_we_done(self):
        return False

    def wrap_up(self):
        pass
