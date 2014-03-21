import os
import pytest
from subprocess import call
from shutil import rmtree

import fjd


class TestBasicExamples(object):
    '''
    Run the main command with some basic examples and check ... 
    '''
    files_dir = 'test-files'
    num_workers = 3
    project = 'fjd-test'

    @pytest.fixture()
    def clean_slate(self):
        if os.path.exists(self.files_dir):
            rmtree(self.files_dir)
        os.mkdir(self.files_dir)

    def test_noexe(self):
        with pytest.raises(SystemExit):
            fjd.Main(exe=None)

    def test_instanceandparameters(self):
        with pytest.raises(SystemExit):
            fjd.Main(exe='ls', instances=3, parameters=(1,2,3))

    def test_simple_cmd(self, clean_slate):
        call('fjd --project {} --exe "touch {}/simpletest.tmp"'\
                .format(self.project, self.files_dir), shell=True)
        assert(os.path.exists('{}/simpletest.tmp'.format(self.files_dir)))

    def test_instances(self, clean_slate):
        fjd.Main(project=self.project, exe='mktemp {}/tmp.XXXXXXXXXXXXXXXXXXXXXXXXXX'\
                     .format(self.files_dir), instances=10)
        assert(len(os.listdir(self.files_dir)) == 10)

    def test_parameters(self, clean_slate):
        for i in xrange(10):
            call('head -c 102400 </dev/urandom >{}/bla{}.txt'\
                 .format(self.files_dir, i), shell=True)
        fjd.Main(exe='cd {}; gzip bla$1.txt'.format(self.files_dir),
                 parameters=range(10), project=self.project)
        # test that they are zipped
        files = os.listdir(self.files_dir)
        files.sort()
        assert(files == ['bla{}.txt.gz'.format(i) for i in xrange(10)])
