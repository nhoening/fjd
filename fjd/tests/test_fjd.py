import os
import pytest
from subprocess import call
from shutil import rmtree

import fjd


class TestBasicExamples(object):
    '''
    Run the main command with some basic examples.
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

    def test_repeat_and_parameters(self):
        with pytest.raises(SystemExit):
            fjd.Main(exe='ls', repeat=3, parameters=(1,2,3))

    def test_simple_cmd(self, clean_slate):
        call('fjd --project {} --exe "touch {}/simpletest.tmp"'\
                .format(self.project, self.files_dir), shell=True)
        assert(os.path.exists('{}/simpletest.tmp'.format(self.files_dir)))

    def test_repeat(self, clean_slate):
        fjd.Main(project=self.project, exe='mktemp {}/tmp.XXXXXXXXXXXXXXXXXXXXXXXXXX'\
                     .format(self.files_dir), repeat=10)
        assert(len(os.listdir(self.files_dir)) == 10)

    def test_parameters(self, clean_slate):
        call("fjd --project {} --exe 'touch {}/bla$1.dat' --parameters 1,2,3"\
                .format(self.project, self.files_dir), shell=True)
        for i in range(1, 4, 1):
            assert(os.path.exists('{}/bla{}.dat'.format(self.files_dir, i)))

    def test_parameters_code(self, clean_slate):
        for i in xrange(10):
            call('head -c 102400 </dev/urandom >{}/bla{}.txt'\
                 .format(self.files_dir, i), shell=True)
        fjd.Main(exe='cd {}; gzip bla$1.txt'.format(self.files_dir),
                 parameters=range(10), project=self.project)
        # test that they are zipped
        files = os.listdir(self.files_dir)
        files.sort()
        assert(files == ['bla{}.txt.gz'.format(i) for i in xrange(10)])

    def test_multiple_parameters_code(self, clean_slate):
        for i in xrange(10):
            call('head -c 102400 </dev/urandom >{}/bla{}.txt'\
                 .format(self.files_dir, i), shell=True)
        p = ['{}#{}'.format(i, l) for i,l in zip(range(10), 'abcdefghij')]
        fjd.Main(exe='cd {}; gzip bla$1.txt; mv bla$1.txt.gz bla$1$2.txt.gz'.format(self.files_dir),
                 parameters=p, project=self.project)
        # test that they are zipped
        files = os.listdir(self.files_dir)
        files.sort()
        assert(files == ['bla{}{}.txt.gz'.format(i,l) for i,l in zip(xrange(10), 'abcdefghij')])

    def test_callback_str(self):
        fjd.Main(exe='echo BLA', repeat=3, callback='touch {}/cb_str'.format(self.files_dir))
        assert(os.path.exists('{}/cb_str'.format(self.files_dir)))

    def test_callback_func(self):
        def touch_cb2():
            call('touch {}/cb_func'.format(self.files_dir), shell=True)
        fjd.Main(exe='echo BLA', repeat=3, callback=touch_cb2)
        assert(os.path.exists('{}/cb_func'.format(self.files_dir)))

