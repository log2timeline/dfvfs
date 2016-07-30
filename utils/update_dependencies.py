#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to update the dependencies in various configuration files."""

import os
import sys

# Change PYTHONPATH to include dfvfs.
sys.path.insert(0, u'.')

import dfvfs.dependencies


class DPKGControllWriter(object):
  """Class to help write a dpkg control file."""

  _PATH = os.path.join(u'config', u'dpkg', u'control')

  _MAINTAINER = (
      u'Log2Timeline maintainers <log2timeline-maintainers@googlegroups.com>')

  _FILE_HEADER = [
      u'Source: dfvfs',
      u'Section: python',
      u'Priority: extra',
      u'Maintainer: {0:s}'.format(_MAINTAINER),
      (u'Build-Depends: debhelper (>= 7), python-all (>= 2.7~), '
       u'python-setuptools, python3-all (>= 3.4~), python3-setuptools'),
      u'Standards-Version: 3.9.5',
      u'X-Python-Version: >= 2.7',
      u'X-Python3-Version: >= 3.4',
      u'Homepage: https://github.com/log2timeline/dfvfs',
      u'']

  _PYTHON2_PACKAGE_HEADER = [
      u'Package: python-dfvfs',
      u'Architecture: all']

  _PYTHON3_PACKAGE_HEADER = [
      u'Package: python3-dfvfs',
      u'Architecture: all']

  _PYTHON_PACKAGE_FOOTER = [
      u'Description: Digital Forensics Virtual File System (dfVFS).',
      (u' dfVFS, or Digital Forensics Virtual File System, provides '
       u'read-only access to'),
      (u' file-system objects from various storage media types and file '
       u'formats. The goal'),
      (u' of dfVFS is to provide a generic interface for accessing '
       u'file-system objects,'),
      (u' for which it uses several back-ends that provide the actual '
       u'implementation of'),
      u' the various storage media types, volume systems and file systems.',
      u'']

  def Write(self):
    """Writes a setup.cfg file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)
    file_content.extend(self._PYTHON2_PACKAGE_HEADER)

    dependencies = dfvfs.dependencies.GetDPKGDepends()
    dependencies = u', '.join(dependencies)
    file_content.append(
        u'Depends: {0:s}, ${{python:Depends}}, ${{misc:Depends}}'.format(
            dependencies))

    file_content.extend(self._PYTHON_PACKAGE_FOOTER)
    file_content.extend(self._PYTHON3_PACKAGE_HEADER)

    dependencies = dfvfs.dependencies.GetDPKGDepends()
    dependencies = u', '.join(dependencies)
    dependencies = dependencies.replace(u'python', u'python3')
    file_content.append(
        u'Depends: {0:s}, ${{python:Depends}}, ${{misc:Depends}}'.format(
            dependencies))

    file_content.extend(self._PYTHON_PACKAGE_FOOTER)

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class SetupCfgWriter(object):
  """Class to help write a setup.cfg file."""

  _PATH = u'setup.cfg'

  _MAINTAINER = (
      u'Log2Timeline maintainers <log2timeline-maintainers@googlegroups.com>')

  _FILE_HEADER = [
      u'[bdist_rpm]',
      u'release = 1',
      u'packager = {0:s}'.format(_MAINTAINER),
      u'doc_files = ACKNOWLEDGEMENTS',
      u'            AUTHORS',
      u'            LICENSE',
      u'            README',
      u'build_requires = python-setuptools']

  def Write(self):
    """Writes a setup.cfg file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = dfvfs.dependencies.GetRPMRequires()
    for index, dependency in enumerate(dependencies):
      if index == 0:
        file_content.append(u'requires = {0:s}'.format(dependency))
      else:
        file_content.append(u'           {0:s}'.format(dependency))

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)

class ToxIniWriter(object):
  """Class to help write a tox.ini file."""

  _PATH = u'tox.ini'

  _FILE_HEADER = [
      u'[tox]',
      u'envlist = py27, py34',
      u'',
      u'[testenv]',
      u'pip_pre = True',
      u'setenv =',
      u'    PYTHONPATH = {toxinidir}',
      u'deps =',
      u'    pip >= 7.0.0',
      u'    pytest']

  _FILE_FOOTER = [
      u'commands = python run_tests.py',
      u'']

  def Write(self):
    """Writes a tox.ini file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    for dependency in dfvfs.dependencies.GetInstallRequires():
      file_content.append(u'    {0:s}'.format(dependency))

    file_content.extend(self._FILE_FOOTER)

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class TravisBeforeInstallScript(object):
  """Class to help write the Travis-CI before_install.sh file."""

  _PATH = os.path.join(
      u'config', u'travis', u'before_install.sh')

  _FILE_HEADER = [
      u'#!/bin/bash',
      u'#',
      u'# Script to set up Travis-CI test VM.',
      u'',
      (u'COVERALL_DEPENDENCIES="python-coverage python-coveralls '
       u'python-docopt";'),
      u'']

  _FILE_FOOTER = [
      u'',
      u'# Exit on error.',
      u'set -e;',
      u'',
      u'if test `uname -s` = "Darwin";',
      u'then',
      u'\tgit clone https://github.com/log2timeline/l2tdevtools.git;',
      u'',
      u'\tmv l2tdevtools ../;',
      u'\tmkdir dependencies;',
      u'',
      u'\tPYTHONPATH=../l2tdevtools ../l2tdevtools/tools/update.py --download-directory=dependencies --preset=dfvfs;',
      u'',
      u'elif test `uname -s` = "Linux";',
      u'then',
      u'\tsudo add-apt-repository ppa:gift/dev -y;',
      u'\tsudo apt-get update -q;',
      (u'\tsudo apt-get install -y ${COVERALL_DEPENDENCIES} '
       u'${PYTHON2_DEPENDENCIES} ${PYTHON3_DEPENDENCIES};'),
      u'fi',
      u'']

  def Write(self):
    """Writes a setup.cfg file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = dfvfs.dependencies.GetDPKGDepends(exclude_version=True)
    dependencies.append(u'python-lzma')
    dependencies = u' '.join(sorted(dependencies))
    file_content.append(u'PYTHON2_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.append(u'')

    dependencies = dfvfs.dependencies.GetDPKGDepends(exclude_version=True)
    dependencies = u' '.join(dependencies)
    dependencies = dependencies.replace(u'python', u'python3')
    file_content.append(u'PYTHON3_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.extend(self._FILE_FOOTER)

    file_content = u'\n'.join(file_content)
    file_content = file_content.encode(u'utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


if __name__ == u'__main__':
  writer = DPKGControllWriter()
  writer.Write()

  writer = SetupCfgWriter()
  writer.Write()

  writer = ToxIniWriter()
  writer.Write()

  writer = TravisBeforeInstallScript()
  writer.Write()
