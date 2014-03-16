import os
import pytest
#from subprocess import call
from shutil import rmtree


class TestBasicExamples(object):
    '''
    Run the basic examples and check ... 
    '''
    ex_dir = 'fjd/example'
    num_workers = 3

    @pytest.fixture(scope='module')
    def run_example(self):
        fjd_dir = os.path.expanduser('~/.fjd/default')
        rmtree('{}/screenlogs'.format(fjd_dir))
        os.chdir(self.ex_dir)
        call('./create_jobs.py', shell=True)
        call('fjd-recruiter hire {}'.format(self.num_workers), shell=True)
        call('fjd-dispatcher --end_when_jobs_are_done', shell=True)


