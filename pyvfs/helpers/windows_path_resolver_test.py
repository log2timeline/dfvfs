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
"""Tests for the Windows path resolver object."""

import os
import unittest

from pyvfs.file_io import qcow_file_io
from pyvfs.helpers import windows_path_resolver
from pyvfs.path import os_path_spec
from pyvfs.path import qcow_path_spec
from pyvfs.vfs import tsk_file_system


class WindowsPathResolverTest(unittest.TestCase):
  """The unit test for the windows path resolver object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_file = os.path.join('test_data', 'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)
    file_object = qcow_file_io.QcowFile()
    file_object.open(self._qcow_path_spec)
    self._tsk_file_system = tsk_file_system.TSKFileSystem(
        file_object, self._qcow_path_spec)

  def testResolvePath(self):
    """Test the resolve path function."""
    path_resolver = windows_path_resolver.WindowsPathResolver(
        self._tsk_file_system, parent=self._qcow_path_spec)

    expected_path = (
        u'/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}')

    windows_path = (
        u'C:\\System Volume Information'
        u'\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.location, expected_path)

    windows_path = (
        u'\\\\?\\C:\\System Volume Information'
        u'\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.location, expected_path)

    windows_path = (
        u'\\\\.\\C:\\System Volume Information'
        u'\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.location, expected_path)

    expected_path = u'/syslog.gz'

    windows_path = u'\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.location, expected_path)

    windows_path = u'C:\\..\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.location, expected_path)

    expected_path = u'/'

    windows_path = u'\\'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.location, expected_path)

    windows_path = u'S'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

    windows_path = u'\\\\?\\'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

    windows_path = u'\\\\.\\'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

    windows_path = u'\\\\?\\UNC\\server\\share\\directory\\file.txt'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

    windows_path = u'\\\\server\\share\\directory\\file.txt'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

    windows_path = u'SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

    windows_path = u'.\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

    windows_path = u'..\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)

  def testResolvePathWithEnvironmentVariable(self):
    """Test the resolve path function."""
    path_resolver = windows_path_resolver.WindowsPathResolver(
        self._tsk_file_system, parent=self._qcow_path_spec)

    path_resolver.SetEnvironmentVariable(
        'SystemRoot', 'C:\\System Volume Information')

    expected_path = (
        u'/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}')

    windows_path = u'%SystemRoot%\\{3808876b-c176-4e48-b7ae-04046e6cc752}'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertNotEquals(path_spec, None)
    self.assertEquals(path_spec.location, expected_path)

    windows_path = u'%WinDir%\\{3808876b-c176-4e48-b7ae-04046e6cc752}'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertEquals(path_spec, None)


if __name__ == '__main__':
  unittest.main()
