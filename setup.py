#!/usr/bin/python
# -*- coding: utf-8 -*-
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
"""
This is the setup file for the project. The standard setup rules apply:

  python setup.py build
  sudo python setup.py install
"""
import glob
import os
import sys

#import run_tests

try:
  from setuptools import find_packages, setup, Command
except ImportError:
  from distutils.core import find_packages, setup, Command

if sys.version < '2.7':
  print ('Wrong Python Version, require version 2.7 or higher (and lower '
         'than 3.X).\n%s') % sys.version
  sys.exit(1)


def GetFileList(path, patterns):
  file_list = []

  for directory, sub_directories, files in os.walk(path):
    for pattern in patterns:
      directory_pattern = os.path.join(directory, pattern)

      for pattern_match in glob.iglob(directory_pattern):
        if os.path.isfile(pattern_match):
          file_list.append(pattern_match)

  return file_list


class TestCommand(Command):
  """Run tests, implementing an interface."""
  user_options = []

  def initialize_options(self):
    self._dir = os.getcwd()

  def finalize_options(self):
    pass

  def run(self):
    pass
    #results = run_tests.RunTests()


setup(name='pyvfs',
      version='1.0.0',
      description=(
          'PyVFS libraries, used to allow read-only access to file like '
          'objects, useable for various scripts and tools.'),
      license='Apache License, Version 2.0',
      url='https://code.google.com/p/pyvfs',
      package_dir={'pyvfs': 'pyvfs'},
      #cmdclass = {'test': TestCommand},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      #include_package_data=True,
      packages=find_packages('.'),
      package_data={'pyvfs.test_data': GetFileList('test_data', ['*'])},
     )

