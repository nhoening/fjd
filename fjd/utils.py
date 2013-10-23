import os
import os.path as osp


def ensure_wdir(project):
    ''' make sure working directory with needed sub-directories exists.'''
    fjd_home = osp.expanduser('~/.fjd')
    if not osp.exists(fjd_home):
        os.mkdir(fjd_home)
    if not osp.exists("{}/{}".format(fjd_home, project)):
        os.mkdir("{}/{}".format(fjd_home, project))
    for d in ('jobqueue', 'jobpod', 'workerqueue'):
        if not osp.exists('{}/{}/{}'.format(fjd_home, project, d)):
            os.mkdir('{}/{}/{}'.format(fjd_home, project, d))
    return "{}/{}".format(fjd_home, project)
 
