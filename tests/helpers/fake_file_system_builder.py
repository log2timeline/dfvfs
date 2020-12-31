#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the fake file system builder object."""

import unittest

from dfvfs.helpers import fake_file_system_builder

from tests import test_lib as shared_test_lib


class FakeFileSystemBuilderTest(shared_test_lib.BaseTestCase):
  """The unit test for the fake file system builder object."""

  def testAddDirectory(self):
    """Tests the AddDirectory function."""
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()

    test_path = '/usr/lib/python2.7/site-packages/dfvfs'
    file_system_builder.AddDirectory(test_path)

    with self.assertRaises(ValueError):
      file_system_builder.AddDirectory(test_path)

  def testAddFile(self):
    """Tests the AddFile function."""
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()

    test_path = '/usr/lib/python2.7/site-packages/dfvfs/__init__.py'
    test_file_data = b'\n'.join([
        b'# -*- coding: utf-8 -*-',
        b'"""Digital Forensics Virtual File System (dfVFS).',
        b'',
        b'dfVFS, or Digital Forensics Virtual File System, is a Python module',
        b'that provides read-only access to file-system objects from various',
        b'storage media types and file formats.',
        b'"""'])

    file_system_builder.AddFile(test_path, test_file_data)

    with self.assertRaises(ValueError):
      file_system_builder.AddFile(test_path, test_file_data)

    test_path = '/usr/bin/empty'
    file_system_builder.AddFile(test_path, b'')

    test_path = '/usr/bin/empty/file'
    with self.assertRaises(ValueError):
      file_system_builder.AddFile(test_path, b'')

  def testAddFileReadData(self):
    """Tests the AddFileReadData function."""
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()

    test_path = '/usr/lib/python2.7/site-packages/dfvfs/__init__.py'
    test_file_data_path = self._GetTestFilePath(['init.py'])
    self._SkipIfPathNotExists(test_file_data_path)

    file_system_builder.AddFileReadData(test_path, test_file_data_path)

    with self.assertRaises(ValueError):
      file_system_builder.AddFileReadData(test_path, test_file_data_path)

  def testAddSymbolicLink(self):
    """Tests the AddSymbolicLink function."""
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()

    test_path = '/usr/lib/python2.7/site-packages/dfvfs'
    test_linked_path = '/opt/dfvfs'
    file_system_builder.AddSymbolicLink(test_path, test_linked_path)

    with self.assertRaises(ValueError):
      file_system_builder.AddSymbolicLink(test_path, test_linked_path)


if __name__ == '__main__':
  unittest.main()
