# -*- coding:iso-8859-1

from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import codecs
import os
import sys
import re


here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.md') + read('CHANGES.txt') + read('TODO')

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
    version=find_version('fjd', '__init__.py'),
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
    scripts = ['fjd/scripts/fjd-dispatcher', 'fjd/scripts/fjd-worker',
              'fjd/scripts/fjd-recruiter', 'fjd/scripts/bgscreen']
)

