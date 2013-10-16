# -*- coding:iso-8859-1

from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import fjd 

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md', 'CHANGES.txt')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='fjd',
    version=fjd.__version__,
    url='http://github.com/nhoening/fjd/',
    license='Apache Software License',
    author='Nicolas Höning',
    tests_require=['pytest'],
    install_requires=['screenutils>=0.0.1.5.4', 'paramiko>=1.7.7.1'],

    cmdclass={'test': PyTest},
    author_email='iam@nicolashoening.de',
    description='File-based job distribution for everyone',
    long_description=long_description,
    packages=['fjd'],
    include_package_data=True,
    platforms='Unix',
    test_suite='fjd.test.test_fjd',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
        ],
    extras_require={
        'testing': ['pytest'],
    },
    scripts = ['fjd/dispatcher.py', 'fjd/worker.py', 'fjd/recruiter.py', 'fjd/bgscreen']
)

