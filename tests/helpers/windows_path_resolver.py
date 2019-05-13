#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows path resolver object."""

from __future__ import unicode_literals

import unittest

from dfvfs.helpers import windows_path_resolver
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import os_file_system
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class WindowsPathResolverTest(shared_test_lib.BaseTestCase):
  """The unit test for the windows path resolver object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

    test_file = self._GetTestFilePath([])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._os_file_system = os_file_system.OSFileSystem(self._resolver_context)

    # TODO: add RAW volume only test image.

    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location='/', parent=self._qcow_path_spec)

    self._tsk_file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context)
    self._tsk_file_system.Open(self._tsk_path_spec)

  def testResolvePathDirectory(self):
    """Test the resolve path function on a mount point directory."""
    path_resolver = windows_path_resolver.WindowsPathResolver(
        self._os_file_system, self._os_path_spec)

    expected_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])

    windows_path = 'C:\\testdir_os\\file1.txt'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    test_windows_path = path_resolver.GetWindowsPath(path_spec)
    self.assertEqual(test_windows_path, windows_path)

    windows_path = 'C:\\testdir_os\\file6.txt'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

  def testResolvePathImage(self):
    """Test the resolve path function on a storage media image."""
    path_resolver = windows_path_resolver.WindowsPathResolver(
        self._tsk_file_system, self._qcow_path_spec)

    expected_path = (
        '/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}')

    windows_path = (
        'C:\\System Volume Information'
        '\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    test_windows_path = path_resolver.GetWindowsPath(path_spec)
    self.assertEqual(test_windows_path, windows_path)

    windows_path = (
        '\\\\?\\C:\\System Volume Information'
        '\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    windows_path = (
        '\\\\.\\C:\\System Volume Information'
        '\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    expected_path = '/syslog.gz'

    windows_path = '\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    windows_path = 'C:\\..\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    expected_path = '/'

    windows_path = '\\'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    windows_path = 'S'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    windows_path = '\\\\?\\'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    windows_path = '\\\\.\\'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    windows_path = '\\\\?\\UNC\\server\\share\\directory\\file.txt'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    windows_path = '\\\\server\\share\\directory\\file.txt'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    windows_path = 'SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    windows_path = '.\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    windows_path = '..\\SYSLOG.GZ'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

  def testResolvePathWithEnvironmentVariable(self):
    """Test the resolve path function with environment variable expansion."""
    path_resolver = windows_path_resolver.WindowsPathResolver(
        self._tsk_file_system, self._qcow_path_spec)

    path_resolver.SetEnvironmentVariable(
        'SystemRoot', 'C:\\System Volume Information')

    expected_path = (
        '/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}')

    windows_path = '%SystemRoot%\\{3808876b-c176-4e48-b7ae-04046e6cc752}'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)

    expected_windows_path = (
        'C:\\System Volume Information'
        '\\{3808876b-c176-4e48-b7ae-04046e6cc752}')
    test_windows_path = path_resolver.GetWindowsPath(path_spec)
    self.assertEqual(test_windows_path, expected_windows_path)

    windows_path = '%WinDir%\\{3808876b-c176-4e48-b7ae-04046e6cc752}'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNone(path_spec)

    # Test resolving multi path segment environment variables.
    path_resolver = windows_path_resolver.WindowsPathResolver(
        self._os_file_system, self._os_path_spec)

    expected_path = self._GetTestFilePath([
        'testdir_os', 'subdir1', 'file6.txt'])

    path_resolver.SetEnvironmentVariable('Test', 'C:\\testdir_os\\subdir1')

    windows_path = '%Test%\\file6.txt'
    path_spec = path_resolver.ResolvePath(windows_path)
    self.assertIsNotNone(path_spec)
    self.assertEqual(path_spec.location, expected_path)


if __name__ == '__main__':
  unittest.main()
