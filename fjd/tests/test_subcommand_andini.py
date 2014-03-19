import os
import pytest
from subprocess import call
from shutil import rmtree

from fjd.utils import ensure_wdir, empty_queues


class QestAdvancedExample(object):
    '''
    Run the advanced example and check that joblogs and logfiles of example are there
    '''
    ex_dir = 'fjd/example/advanced'
    num_workers = 3

    @pytest.fixture(scope='module')
    def run_example(self):
        fjd_dir = os.path.expanduser('~/.fjd/default')
        ensure_wdir()
        empty_queues()
        os.chdir(self.ex_dir)
        if os.path.exists('logfiles'):
            rmtree('logfiles')
        os.mkdir('logfiles')
        call('./create_jobs.py', shell=True)
        call('fjd-recruiter hire {}'.format(self.num_workers), shell=True)
        call('fjd-dispatcher --end_when_jobs_are_done', shell=True)

    def test_jobs(self, run_example):
        fjd_dir = os.path.expanduser('~/.fjd/default')
        assert(os.path.exists('{}/screenlogs'.format(fjd_dir)))
        logs = os.listdir('{}/screenlogs'.format(fjd_dir))
        assert(len(logs) == self.num_workers)
        for lf in logs:
            log = open('{}/screenlogs/{}'.format(fjd_dir, lf), 'r').read()
            assert('I found a job' in log)
            assert('Finished my job' in log)

    # TODO: needed?
    def test_data(self, run_example):
        assert(os.path.exists('logfiles'))
        data = os.listdir('logfiles')
        data.sort()
        assert(data == ['job' + str(i) + '.dat' for i in xrange(10)])

