#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pybde."""

import os
import unittest

from dfvfs.path import bde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import bde_file_system


class BDEFileSystemTest(unittest.TestCase):
  """The unit test for the BDE file system object."""

  _BDE_PASSWORD = u'bde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'bdetogo.raw')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._bde_path_spec = bde_path_spec.BDEPathSpec(parent=path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._bde_path_spec, u'password', self._BDE_PASSWORD)

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = bde_file_system.BDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._bde_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = bde_file_system.BDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._bde_path_spec)

    self.assertTrue(file_system.FileEntryExistsByPathSpec(self._bde_path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = bde_file_system.BDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._bde_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(self._bde_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = bde_file_system.BDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._bde_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, u'')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
