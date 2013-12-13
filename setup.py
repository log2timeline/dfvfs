#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Installation and deployment script."""

import glob
import os
import sys

import run_tests

try:
  from setuptools import find_packages, setup, Command
except ImportError:
  from distutils.core import find_packages, setup, Command

if sys.version < '2.7':
  print 'Unsupported Python version: {0:s}.'.format(sys.version)
  print 'Supported Python versions are 2.7 or a later 2.x version.'
  sys.exit(1)


class TestCommand(Command):
  """Run tests, implementing an interface."""
  user_options = []

  def initialize_options(self):
    self._dir = os.getcwd()

  def finalize_options(self):
    pass

  def run(self):
    test_results = run_tests.RunTests(os.path.join('.', 'pyvfs'))


setup(
    name='pyvfs',
    version='1.0.0',
    description=(
        'PyVFS is a Python module used to provide a read-only Virtual File '
        'System (VFS) for various file system and file formats.'),
    license='Apache License, Version 2.0',
    url='https://code.google.com/p/pyvfs',
    maintainer_email='log2timeline-dev@googlegroups.com',
    cmdclass = {'test': TestCommand},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    package_dir={'pyvfs': 'pyvfs'},
    packages=find_packages('.'),
)
