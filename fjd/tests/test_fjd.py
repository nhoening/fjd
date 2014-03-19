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
    
    @pytest.fixture(scope='module')
    def prepare(self):
        if os.path.exists(self.files_dir):
            rmtree(self.files_dir)
        os.mkdir(self.files_dir)
    
    def test_noexe(self, prepare):
        with pytest.raises(Exception):
            fjd.Main(exe=None)

    def test_instanceandparameters(self, prepare):
        with pytest.raises(Exception):
            fjd.Main(exe='ls', instances=3, parameters=(1,2,3))

    def test_instances(self, prepare):
        fjd.Main(exe='mktemp {}/tmp.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'\
                     .format(self.files_dir), instances=10)     
        assert(len(os.listdir(self.files_dir) == 10))

    def test_parameters(self, prepare):
        print(os.listdir('.'))
        for i in xrange(10):
            call('head -c 1048576 </dev/urandom >{}/bla{}.txt'\
                 .format(self.files_dir, i))
        fjd.Main(exe='gzip $1', parameters=list(range(10)))
        # test that they are zipped
        files = os.listdir(self.files_dir)
        files.sort()
        assert(files == ['bla{}.txt.gz'.format(i) for i in xrange(10)])
