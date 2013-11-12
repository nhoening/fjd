#!/usr/bin/env python

import os
import os.path as osp
from getpass import getuser
from subprocess import Popen
from screenutils import list_screens #, Screen
from ConfigParser import ConfigParser

from fjd.sshtools import mk_ssh_client, ssh
from fjd.utils import ensure_wdir


debug = False


class Recruiter(object):

    def __init__(self, num_workers=1, project=None, local_only=False):
        if not project:
            project = 'default'
        self.project = project
        self.wdir = ensure_wdir(project)

        # build up self.hosts
        self.hosts = [dict(name='localhost', workers=int(num_workers))]
        rc_loc = "{}/remote.conf".format(self.wdir)
        if osp.exists(rc_loc) and not local_only:
            self.hosts = []
            remote_conf = ConfigParser()
            remote_conf.read(rc_loc)
            num_hosts = 0
            while remote_conf.has_section('host{}'.format(num_hosts + 1)):
                hid = "host{}".format(num_hosts + 1)
                if not remote_conf.has_option(hid, 'name') or\
                   not remote_conf.has_option(hid, 'workers'):
                    print("[fjd-recruiter] Host section for {} is missing"\
                          " name or workers option!".format(hid))
                else:
                    self.hosts.append(
                        dict(name=remote_conf.get(hid, "name"),
                             workers=remote_conf.getint(hid, "workers")))
                num_hosts += 1
            if debug:
                print("[fjd-recruiter] I am configured with hosts {}."\
                    .format(','.join([h['name'] for h in self.hosts])))

    def hire(self):
        if len(self.hosts) == 0:
            print("[fjd-recruiter] Not sufficiently intialised to hire!")
            return
        self.fire(local_only=True)
        for host in self.hosts:
            if host['name'] == 'localhost':
                for worker in range(host['workers']):
                    sid = "{}-{}-{}".format(self.project,
                                            self.hosts.index(host) + 1,
                                            worker + 1)
                    # This below is not working well (screen blinks), and 
                    # with the manual way we get more precision in creating screens
                    #s = Screen(sid, True)
                    #s.send_commands('bash')
                    #s.send_commands('python fjd/worker.py')
                    Popen('bgscreen {} "fjd-worker --project {}"'\
                              .format(sid, self.project), shell=True).wait()
                print('[fjd-recruiter] Hired {} workers in project "{}".'\
                       .format(host['workers'], self.project))
            else:
                # for remote hosts, call the recruiter over there
                ssh_client = mk_ssh_client(host['name'], getuser())
                print("[fjd-recruiter] Host {}: {}".format(host['name'],
                        ssh(ssh_client, 'fjd-recruiter --project {} --local-only hire {}'\
                            .format(self.project, host['workers'])).strip().replace('\n', '\n        ....')))

    def fire(self, local_only=False):
        if len(self.hosts) == 0:
            print("[fjd-recruiter] No configured workers that I could search for!")
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
                    print('[fjd-recruiter] Fired {} workers in project "{}".'\
                            .format(fired, self.project))
                elif debug:
                    print('[fjd-recruiter] No workers busy (yet) in project "{}".'\
                            .format(self.project))
            elif not local_only:
                # for remote hosts, call the recruiter over there
                ssh_client = mk_ssh_client(host['name'], getuser())
                print("[fjd-recruiter] Host {}: {}".format(host['name'],
                        ssh(ssh_client, 'fjd-recruiter --local-only --project {} fire'\
                                  .format(self.project)).strip().replace('\n', '\n        ....')))

