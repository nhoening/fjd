#!/usr/bin/python

import sys
import time
import random
try:
    import configparser
except ImportError:
    import ConfigParser as configparser  # for py2


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: ./{} <conf-filename>".format(sys.argv[0])
        sys.exit()
    conf = configparser.ConfigParser()
    conf.read(sys.argv[1])
    time.sleep(random.randint(0, 3))  # pretend we're doing real work
    outfile = open(conf.get('params', 'logfile'), 'w')
    val = conf.get('params', 'my_param')
    outfile.write('This was done with parameter my_param:{val}.'.format(val=val))
    outfile.close()
