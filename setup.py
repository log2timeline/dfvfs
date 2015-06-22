#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Installation and deployment script."""

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

# Change PYTHONPATH to include dfvfs so that we can get the version.
sys.path.insert(0, '.')

import dfvfs


class TestCommand(Command):
  """Run tests, implementing an interface."""
  user_options = []

  def initialize_options(self):
    self._dir = os.getcwd()

  def finalize_options(self):
    pass

  def run(self):
    test_results = run_tests.RunTests(os.path.join('.', 'dfvfs'))


dfvfs_version = dfvfs.__version__

# Command bdist_msi does not support the library version, neither a date
# as a version but if we suffix it with .1 everything is fine.
if 'bdist_msi' in sys.argv:
  dfvfs_version += '.1'

dfvfs_description = (
    'Digital Forensics Virtual File System (dfVFS).')

dfvfs_long_description = (
    'dfVFS, or Digital Forensics Virtual File System, is a Python module '
    'that provides read-only access to file-system objects from various '
    'storage media types and file formats.')

setup(
    name='dfvfs',
    version=dfvfs_version,
    description=dfvfs_description,
    long_description=dfvfs_long_description,
    license='Apache License, Version 2.0',
    url='https://github.com/log2timeline/dfvfs',
    maintainer='dfVFS development team',
    maintainer_email='log2timeline-dev@googlegroups.com',
    cmdclass={'test': TestCommand},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=find_packages('.', exclude=[u'examples', u'tests', u'tests.*']),
    package_dir={
        'dfvfs': 'dfvfs'
    },
    data_files=[
        ('share/doc/dfvfs', [
            u'AUTHORS', u'ACKNOWLEDGEMENTS', u'LICENSE', u'README']),
    ],
)
