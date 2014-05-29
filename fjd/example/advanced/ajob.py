#!/usr/bin/python

import sys
import time
import random


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ./{} <index> <log-file-name>".format(sys.argv[0]))
        sys.exit()
    time.sleep(random.randint(0, 3))  # pretend we're doing real work
    outfile = open(sys.argv[2], 'w')
    outfile.write('This was done with parameter my_param:{val}.'.format(val=sys.argv[1]))
    outfile.close()
