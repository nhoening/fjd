import os
import pytest
from subprocess import call
from shutil import rmtree

from fjd.utils import ensure_wdir, empty_queues


class TestAdvancedExample(object):
    '''
    Run the advanced example and check that joblogs and logfiles of example are there
    '''
    ex_dir = 'fjd/example/advanced'
    num_workers = 3
    project = 'fjd-advanced-test'

    @pytest.fixture(scope='module')
    def run_example(self):
        ensure_wdir(project=self.project)
        empty_queues(project=self.project)
        os.chdir(self.ex_dir)
        if os.path.exists('logfiles'):
            rmtree('logfiles')
        os.mkdir('logfiles')
        call('./create_jobs.py {}'.format(self.project), shell=True)
        call('fjd-recruiter --project {} hire {}'\
                .format(self.project, self.num_workers), shell=True)
        call('fjd-dispatcher --project {} --end_when_jobs_are_done'\
                .format(self.project), shell=True)

    def test_jobs(self, run_example):
        fjd_dir = os.path.expanduser('~/.fjd/{}'.format(self.project))
        assert(os.path.exists('{}/screenlogs'.format(fjd_dir)))
        logs = os.listdir('{}/screenlogs'.format(fjd_dir))
        assert(len(logs) == self.num_workers)
        for lf in logs:
            log = open('{}/screenlogs/{}'.format(fjd_dir, lf), 'r').read()
            assert('I found a job' in log)
            assert('Finished my job' in log)

    def test_data(self, run_example):
        assert(os.path.exists('logfiles'))
        data = os.listdir('logfiles')
        data.sort()
        assert(data == ['job' + str(i) + '.dat' for i in range(10)])
        for i in range(10):
            with open('logfiles/job' + str(i) + '.dat', 'r') as lf:
                assert('This was done with parameter my_param:value{val}.'.format(val=i) in lf.read())

