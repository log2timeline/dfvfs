#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Overlay file system implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import overlay_file_system

from tests import test_lib as shared_test_lib


class OverlayFileSystemTestWithEXT4(shared_test_lib.BaseTestCase):
  """Tests the Overlay file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['overlay.dd'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._lower_path_spec = [path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/lower',
        parent=self._raw_path_spec)]
    self._upper_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/upper',
        parent=self._raw_path_spec)
    self._overlay_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/')

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=25)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=ext_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/upper/bogus.txt', inode=100)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/bogus.txt',
        parent=ext_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=25)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=ext_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'c.txt')

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, inode=27,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'd.txt')

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/upper/bogus.txt', inode=100)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/bogus.txt',
        parent=ext_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')


class OverlayFileSystemTestWithXFS(shared_test_lib.BaseTestCase):
  """Tests the Overlay file system."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['overlay_xfs.dd'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._lower_path_spec = [path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, location='/lower',
        parent=self._raw_path_spec)]
    self._upper_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, location='/upper',
        parent=self._raw_path_spec)
    self._overlay_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/')

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenAndClose(self):
    """Test the open and close functionality."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=25)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=ext_path_spec)
    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/upper/bogus.txt', inode=100)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/bogus.txt',
        parent=ext_path_spec)
    self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Tests the GetFileEntryByPathSpec function."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=25)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=ext_path_spec)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'c.txt')

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, inode=27,
        location='/upper/testdir/d.txt', parent=self._raw_path_spec)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/testdir/d.txt',
        parent=ext_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    self.assertIsNotNone(file_entry)

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, 'd.txt')

    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/upper/bogus.txt', inode=100)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/bogus.txt',
        parent=ext_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertIsNone(file_entry)

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)
    self.assertIsNotNone(file_system)

    file_system.Open()

    file_entry = file_system.GetRootFileEntry()

    self.assertIsNotNone(file_entry)
    self.assertEqual(file_entry.name, '')


if __name__ == '__main__':
  unittest.main()
