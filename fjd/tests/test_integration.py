import os
import pytest
import subprocess
from shutil import rmtree


class TestBasicExample(object):
    '''
    Run the basic example and check that joblogs and logfiles of example are there
    '''
    ex_dir = 'fjd/example'

    @pytest.fixture(scope='module')
    def run_example(self):
        os.chdir(self.ex_dir)
        rmtree('logfiles')
        os.mkdir('logfiles')
        subprocess.call('./create_jobs.py', shell=True)
        subprocess.call('fjd-recruiter hire 3', shell=True)
        subprocess.call('fjd-dispatcher --end_when_jobs_are_done', shell=True)

    def test_jobs(self, run_example):
        fjd_dir = os.path.expanduser('~/.fjd/default')
        print('{}/screenlogs'.format(fjd_dir))
        print(os.listdir(fjd_dir))
        assert(os.path.exists('{}/screenlogs'.format(fjd_dir)))
        logs = os.listdir('{}/screenlogs'.format(fjd_dir))
        assert(len(logs) == 3)
        for lf in logs:
            log = open('{}/screenlogs/{}'.format(fjd_dir, lf), 'r').read()
            assert('I found a job' in log)
            assert('Finished my job' in log)

    def test_data(self, run_example):
        assert(os.path.exists('logfiles'))
        data = os.listdir('logfiles')
        data.sort()
        assert(data == ['job' + str(i) + '.dat' for i in xrange(10)])

