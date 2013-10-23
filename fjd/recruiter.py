#!/usr/bin/env python

import os
import os.path as osp
from screenutils import list_screens #, Screen
from ConfigParser import ConfigParser

from fjd.sshtools import mk_ssh_client, ssh
from fjd.utils import ensure_wdir


class Recruiter(object):

    def __init__(self, num_workers=1, project=None):
        if not project:
            project = 'default'
        self.project = project
        self.wdir = ensure_wdir(project)

        self.hosts = [dict(name='localhost', workers=int(num_workers))]
        rc_loc = "{}/{}/remote.conf".format(self.wdir, self.project)
        if osp.exists(rc_loc):
            print("[FJD] Reading in {} ...".format(rc_loc))
            self.hosts = []
            remote_conf = ConfigParser()
            remote_conf.read(rc_loc)
            num_hosts = 0
            while remote_conf.has_section('host{}'.format(num_hosts + 1)):
                hid = "host{}".format(num_hosts + 1)
                self.hosts.append(
                 dict(name=remote_conf.getint(hid, "name"),
                      user=remote_conf.getint(hid, "user"),
                      workers=remote_conf.getint(hid, "workers")))
                num_hosts += 1

    def hire(self):
        if len(self.hosts) == 0:
            print("[FJD] Recruiter not sufficiently intialised to hire!")
            return
        for host in self.hosts:
            if host['name'] == 'localhost':
                self.fire()
                for worker in range(host['workers']):
                    sid = "{}-{}-{}".format(self.project, 
                                            self.hosts.index(host) + 1,
                                            worker + 1)
                    # This below is not working well, TODO, until then we use a script
                    #s = Screen(sid, True)
                    #s.send_commands('bash')
                    #s.send_commands('python fjd/worker.py')
                    os.system('bgscreen {} "fjd-worker --project {}"'\
                              .format(sid, self.project))
                print('[FJD] Hired {} workers in project "{}" on {}.'\
                       .format(host['workers'], self.project, host['name']))
            else:
                # for remote hosts, call the recruiter locally
                ssh_client = mk_ssh_client(host['name'], host['username'])
                ssh(ssh_client, 'fjd-recruiter hire {} --project {}'\
                                 .format(host['workers'], self.project)) 

    def fire(self):
        if len(self.hosts) == 0:
            print("[FJD] No configured workers that I could search for!")
            return
        for host in self.hosts:
            if host['name'] == 'localhost':
                fired = 0
                for s in [s for s in list_screens()\
                          if s.name.startswith(self.project)]:
                    s.kill()
                    fired += 1
                if fired > 0:
                    for f in os.listdir('{}/workerqueue'.format(self.wdir)):
                        os.remove('{}/workerqueue/{}'.format(self.wdir, f))
                    print('[FJD] Fired {} workers in project "{}" on {}.'\
                            .format(fired, self.project, host['name']))
                else:
                    print('[FJD] No workers busy in project "{}" on {}.'\
                            .format(self.project, host['name']))
            else:
                # for remote hosts, call the recruiter locally
                ssh_client = mk_ssh_client(host['name'], host['username'])
                ssh(ssh_client, 'fjd-recruiter fire') 

