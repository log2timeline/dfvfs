#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pyfsntfs."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import ntfs_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import ntfs_file_system

from tests import test_lib as shared_test_lib


class NTFSFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the NTFS file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._ntfs_path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\', parent=self._qcow_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ntfs_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ntfs_path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\password.txt', mft_attribute=1, mft_entry=41,
        parent=self._qcow_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\bogus.txt', mft_entry=19, parent=self._qcow_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ntfs_path_spec)

    path_spec = ntfs_path_spec.NTFSPathSpec(
        mft_attribute=1, mft_entry=41, parent=self._qcow_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    # There is no way to determine the file_entry.name without a location string
    # in the path_spec or retrieving the file_entry from its parent.

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\password.txt', mft_entry=41, parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'password.txt')

    path_spec = ntfs_path_spec.NTFSPathSpec(
        location='\\bogus.txt', mft_entry=19, parent=self._qcow_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

    file_system.Close()

  # TODO: add tests for GetNTFSFileEntryByPathSpec function.

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = ntfs_file_system.NTFSFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._ntfs_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
