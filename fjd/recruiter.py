#!/usr/bin/env python

import os
import os.path as osp
from getpass import getuser
import subprocess
from socket import gethostname
from screenutils import list_screens #, Screen
from ConfigParser import ConfigParser

from fjd.sshtools import mk_ssh_client, ssh
from fjd.utils import ensure_wdir


debug = False


class Recruiter(object):

    def __init__(self, num_workers=1, project=None, local_only=False, curdir=''):
        if not project:
            project = 'default'
        self.project = project
        self.curdir = curdir
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
        curdir = True and self.curdir or os.path.abspath(os.curdir)
        for host in self.hosts:
            if host['name'] == 'localhost':
                for worker in range(host['workers']):
                    sid = "{}-{}-{}".format(self.project, gethostname(), worker + 1)
                    # We create screens manually (not with screenutils), as
                    # we get more precision this way (making an .rc file)
                    rcfile = '{}/screenrcs/{}.rc'.format(self.wdir, sid)
                    logfile = '{}/screenlogs/{}.log'.format(self.wdir, sid)
                    rcf = open(rcfile, 'w')
                    rcf.write('''deflog on
logfile {}
logfile flush 2'''.format(logfile)) # last line flushes to logfile every 2 seconds
                    rcf.close()
                    subprocess.call('bgscreen {} {} "cd {}; fjd-worker --project {}"'\
                            .format(sid, rcfile, curdir, self.project), shell=True)
                print('[fjd-recruiter] Hired {} workers in project "{}".'\
                       .format(host['workers'], self.project))
            else:
                # for remote hosts, call the recruiter over there
                ssh_client = mk_ssh_client(host['name'], getuser())
                print("[fjd-recruiter] Host {}: {}".format(host['name'],
                    ssh(ssh_client, 'fjd-recruiter --project {} --local-only --curdir {} hire {}'\
                          .format(self.project, curdir, host['workers']))\
                        .strip().replace('\n', '\n        ....')))

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

