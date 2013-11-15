import os
import os.path as osp


def ensure_wdir(project='default'):
    '''
    Makes sure working directory with needed sub-directories exists.
    Returns path to project directory.
    '''
    if project == '':
        project = 'default'
    fjd_home = osp.expanduser('~/.fjd')
    if not osp.exists(fjd_home):
        os.mkdir(fjd_home)
    if not osp.exists("{}/{}".format(fjd_home, project)):
        os.mkdir("{}/{}".format(fjd_home, project))
    for d in ('jobqueue', 'jobpod', 'workerqueue', 'screenrcs', 'screenlogs'):
        full_d = '{}/{}/{}'.format(fjd_home, project, d) 
        if not osp.exists(full_d):
            os.mkdir(full_d)
    return "{}/{}".format(fjd_home, project)


def empty_queues(project='default'):
    '''
    Empty the queues - creates a blank state
    '''
    if project == '':
        project = 'default'
    fjd_home = osp.expanduser('~/.fjd')
    if osp.exists(fjd_home):
        if osp.exists("{}/{}".format(fjd_home, project)):
            for d in ('jobqueue', 'jobpod', 'workerqueue', 'screenrcs', 'screenlogs'):
                full_d = '{}/{}/{}'.format(fjd_home, project, d) 
                for f in os.listdir(full_d):
                    os.remove("{}/{}".format(full_d, f))

