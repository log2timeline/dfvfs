#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pybde."""

import os
import unittest

import pybde

from dfvfs.file_io import os_file_io
from dfvfs.path import bde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import bde_file_system


class BdeFileSystemTest(unittest.TestCase):
  """The unit test for the BDE file system object."""

  _BDE_PASSWORD = 'bde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join('test_data', 'bdetogo.raw')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._os_file_object = os_file_io.OSFile(self._resolver_context)
    self._os_file_object.open(self._os_path_spec, mode='rb')

  def testIntialize(self):
    """Test the intialize functionality."""
    bde_volume = pybde.volume()
    bde_volume.set_password(self._BDE_PASSWORD)
    bde_volume.open_file_object(self._os_file_object)
    file_system = bde_file_system.BdeFileSystem(
        self._resolver_context, bde_volume, self._os_path_spec)

    self.assertNotEquals(file_system, None)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    bde_volume = pybde.volume()
    bde_volume.set_password(self._BDE_PASSWORD)
    bde_volume.open_file_object(self._os_file_object)
    file_system = bde_file_system.BdeFileSystem(
        self._resolver_context, bde_volume, self._os_path_spec)

    path_spec = bde_path_spec.BdePathSpec(parent=self._os_path_spec)

    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    bde_volume = pybde.volume()
    bde_volume.set_password(self._BDE_PASSWORD)
    bde_volume.open_file_object(self._os_file_object)
    file_system = bde_file_system.BdeFileSystem(
        self._resolver_context, bde_volume, self._os_path_spec)

    path_spec = bde_path_spec.BdePathSpec(parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    bde_volume = pybde.volume()
    bde_volume.set_password(self._BDE_PASSWORD)
    bde_volume.open_file_object(self._os_file_object)
    file_system = bde_file_system.BdeFileSystem(
        self._resolver_context, bde_volume, self._os_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')


if __name__ == '__main__':
  unittest.main()
