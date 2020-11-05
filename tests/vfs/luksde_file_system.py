#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pyluksde."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import luksde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import luksde_file_system

from tests import test_lib as shared_test_lib


class LUKSDEFileSystemTest(shared_test_lib.BaseTestCase):
  """Tests the LUKSDE file system."""

  _LUKSDE_PASSWORD = 'luksde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['luks1.raw'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._luksde_path_spec = luksde_path_spec.LUKSDEPathSpec(parent=path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._luksde_path_spec, 'password', self._LUKSDE_PASSWORD)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = luksde_file_system.LUKSDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._luksde_path_spec)

    file_system.Close()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = luksde_file_system.LUKSDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._luksde_path_spec)

    self.assertTrue(file_system.FileEntryExistsByPathSpec(
        self._luksde_path_spec))

    file_system.Close()

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = luksde_file_system.LUKSDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._luksde_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(self._luksde_path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = luksde_file_system.LUKSDEFileSystem(self._resolver_context)
    self.assertIsNotNone(file_system)

    file_system.Open(self._luksde_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')

    file_system.Close()


if __name__ == '__main__':
  unittest.main()
