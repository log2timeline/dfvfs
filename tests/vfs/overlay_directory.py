#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Overlay directory implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import overlay_directory
from dfvfs.vfs import overlay_file_system
from dfvfs.path import overlay_path_spec
from tests import test_lib as shared_test_lib


class OverlayDirectoryTest(shared_test_lib.BaseTestCase):
  """Tests the Overlay directory."""

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

    self._file_system = overlay_file_system.OverlayFileSystem(
        self._resolver_context, self._overlay_path_spec,
        self._lower_path_spec, self._upper_path_spec)

    self._file_system.Open()

    self._overlay_root_entry = self._file_system.GetRootFileEntry()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testInitialize(self):
    """Tests the __init__ function."""
    directory = overlay_directory.OverlayDirectory(
        self._file_system, self._overlay_root_entry)

    self.assertIsNotNone(directory)

  def testEntriesGenerator(self):
    """Tests the _EntriesGenerator function."""
    directory = overlay_directory.OverlayDirectory(
        self._file_system, self._overlay_root_entry.path_spec)

    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 5)
    self.assertEqual(entries[0].location, '/c.txt')
    self.assertEqual(entries[0].parent.location, '/upper/c.txt')
    self.assertEqual(entries[0].parent.inode, 25)
    self.assertEqual(entries[1].location, '/testdir')
    self.assertEqual(entries[1].parent.location, '/upper/testdir')
    self.assertEqual(entries[1].parent.inode, 26)
    self.assertEqual(entries[2].location, '/newdir')
    self.assertEqual(entries[2].parent.location, '/upper/newdir')
    self.assertEqual(entries[2].parent.inode, 28)
    self.assertEqual(entries[3].location, '/replacedir')
    self.assertEqual(entries[3].parent.location, '/upper/replacedir')
    self.assertEqual(entries[3].parent.inode, 30)
    self.assertEqual(entries[4].location, '/a.txt')
    self.assertEqual(entries[4].parent.location, '/lower/a.txt')
    self.assertEqual(entries[4].parent.inode, 16)

    overlay_path = overlay_path_spec.OverlayPathSpec(location='/replacedir')
    directory = overlay_directory.OverlayDirectory(
        self._file_system, overlay_path)
    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)
    self.assertEqual(entries[0].location, '/replacedir/replace2.txt')
    self.assertEqual(entries[0].parent.location,
                     '/upper/replacedir/replace2.txt')
    self.assertEqual(entries[0].parent.inode, 32)

    overlay_path = overlay_path_spec.OverlayPathSpec(location='/newdir')
    directory = overlay_directory.OverlayDirectory(
        self._file_system, overlay_path)
    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 1)
    self.assertEqual(entries[0].location, '/newdir/e.txt')
    self.assertEqual(entries[0].parent.location, '/upper/newdir/e.txt')
    self.assertEqual(entries[0].parent.inode, 29)

    overlay_path = overlay_path_spec.OverlayPathSpec(location='/testdir')
    directory = overlay_directory.OverlayDirectory(
        self._file_system, overlay_path)
    self.assertIsNotNone(directory)

    entries = list(directory.entries)
    self.assertEqual(len(entries), 2)
    self.assertEqual(entries[0].location, '/testdir/d.txt')
    self.assertEqual(entries[0].parent.location, '/upper/testdir/d.txt')
    self.assertEqual(entries[0].parent.inode, 27)
    self.assertEqual(entries[1].location, '/testdir/b.txt')
    self.assertEqual(entries[1].parent.location, '/lower/testdir/b.txt')
    self.assertEqual(entries[1].parent.inode, 23)


if __name__ == '__main__':
  unittest.main()
