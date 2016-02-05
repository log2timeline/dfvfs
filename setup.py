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

try:
  from setuptools.commands.bdist_rpm import bdist_rpm
except ImportError:
  from distutils.command.bdist_rpm import bdist_rpm

if sys.version < '2.7':
  print('Unsupported Python version: {0:s}.'.format(sys.version))
  print('Supported Python versions are 2.7 or a later 2.x version.')
  sys.exit(1)

# Change PYTHONPATH to include dfvfs so that we can get the version.
sys.path.insert(0, '.')

import dfvfs


class BdistRPMCommand(bdist_rpm):
  """Custom handler for the bdist_rpm command."""

  def _make_spec_file(self):
    """Generates the text of an RPM spec file.

    Returns:
      A list of strings containing the lines of text.
    """
    # Note that bdist_rpm can be an old style class.
    if issubclass(BdistRPMCommand, object):
      spec_file = super(BdistRPMCommand, self)._make_spec_file()
    else:
      spec_file = bdist_rpm._make_spec_file(self)

    if sys.version_info[0] < 3:
      python_package = 'python'
    else:
      python_package = 'python3'

    description = []
    summary = ''
    in_description = False

    python_spec_file = []
    for index, line in enumerate(spec_file):
      if line.startswith('Summary: '):
        summary = line

      elif line.startswith('BuildRequires: '):
        line = 'BuildRequires: {0:s}-setuptools'.format(python_package)

      elif line.startswith('Requires: '):
        if python_package == 'python3':
          line = line.replace('python-backports-lzma', '')
          line = line.replace('python', 'python3')

      elif line.startswith('%description'):
        in_description = True

      elif line.startswith('%files'):
        line = '%files -f INSTALLED_FILES -n {0:s}-%{{name}}'.format(
           python_package)

      elif line.startswith('%prep'):
        in_description = False

        python_spec_file.append(
            '%package -n {0:s}-%{{name}}'.format(python_package))
        python_spec_file.append('{0:s}'.format(summary))
        python_spec_file.append('')
        python_spec_file.append(
            '%description -n {0:s}-%{{name}}'.format(python_package))
        python_spec_file.extend(description)

      elif in_description:
        # Ignore leading white lines in the description.
        if not description and not line:
          continue

        description.append(line)

      python_spec_file.append(line)

    return python_spec_file


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
    cmdclass={
        'bdist_rpm': BdistRPMCommand,
        'test': TestCommand},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=find_packages('.', exclude=[
        'examples', 'tests', 'tests.*', 'utils']),
    package_dir={
        'dfvfs': 'dfvfs'
    },
    data_files=[
        ('share/doc/dfvfs', [
            'AUTHORS', 'ACKNOWLEDGEMENTS', 'LICENSE', 'README']),
    ],
)
