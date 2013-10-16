#!/usr/bin/env python

import sys
import os
import os.path as osp
from screenutils import list_screens #, Screen
from ConfigParser import ConfigParser

from fjd.sshtools import mk_ssh_client, ssh


class Recruiter(object):

    def __init__(self, num_workers=1, remote_conf_location=None,
                 group='fdj-worker'):
        self.group = group

        self.hosts = [dict(name='localhost', workers=int(num_workers))]
        if remote_conf_location:
            self.hosts = []
            if osp.exists(remote_conf_location):
                remote_conf = ConfigParser()
                remote_conf.read(remote_conf_location)
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
                    sid = "{}-{}-{}".format(self.group, 
                                            self.hosts.index(host) + 1,
                                            worker + 1)
                    # This below is not working well, TODO, until then we use a script
                    #s = Screen(sid, True)
                    #s.send_commands('bash')
                    #s.send_commands('python fjd/worker.py')
                    os.system('bgscreen {} "worker.py"'.format(sid))
                print('[FJD] Hired {} workers on {}.'.format(host['workers'],
                                                             host['name']))
            else:
                # for remote hosts, call the recruiter locally
                ssh_client = mk_ssh_client(host['name'], host['username'])
                ssh(ssh_client, 'recruiter.py hire {}'\
                                 .format(host['workers'])) 

    def fire(self):
        if len(self.hosts) == 0:
            print("[FJD] No configured workers that I could search for!")
            return
        for host in self.hosts:
            if host['name'] == 'localhost':
                fired = 0
                for s in [s for s in list_screens()\
                          if s.name.startswith(self.group)]:
                    s.kill()
                    fired += 1
                if fired > 0:
                    print('[FJD] Fired {} workers on {}.'.format(fired,
                                                                 host['name']))
            else:
                # for remote hosts, call the recruiter locally
                ssh_client = mk_ssh_client(host['name'], host['username'])
                ssh(ssh_client, 'recruiter.py fire') 


if __name__ == '__main__':
    '''
    Start some workers on this PC
    ''' 
    a = sys.argv
    if len(a) <= 1\
       or (len(a) == 3 and a[1] != "hire")\
       or (len(a) == 2 and a[1] != "fire"):
        print("[FJD] usage: python recruiter.py {hire <num_workers>, fire}")
        sys.exit(2)
    if a[1] == 'hire':
        recruiter = Recruiter(num_workers = int(a[2]))
        recruiter.hire()
    elif a[1] == 'fire':
        recruiter = Recruiter()
        recruiter.fire()
