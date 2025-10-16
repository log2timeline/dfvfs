#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Overlay File System file-like object."""

import os
import unittest

from dfvfs.file_io import overlay_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


class OverlayFileWithEXT4Test(shared_test_lib.BaseTestCase):
  """Tests the file-like object implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(OverlayFileWithEXT4Test, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['overlay_ext4.dd'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=25)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=ext_path_spec)

    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 9)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      file_object.Open()

  def testSeek(self):
    """Test the seek functionality."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/upper/newdir/e.txt', inode=29)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/newdir/e.txt',
        parent=ext_path_spec)

    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 28)

    file_object.seek(2)
    self.assertEqual(file_object.read(2), b'is')
    self.assertEqual(file_object.get_offset(), 4)

    file_object.seek(-9, os.SEEK_END)
    self.assertEqual(file_object.read(4), b'over')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEqual(file_object.read(2), b'y!')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(300, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), 300)
    self.assertEqual(file_object.read(2), b'')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

  def testRead(self):
    """Test the read functionality."""
    ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, parent=self._raw_path_spec,
        location='/lower/a.txt', inode=16)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/a.txt',
        parent=ext_path_spec)
    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    file_object.Open()
    read_buffer = file_object.read()

    expected_buffer = b'aaaaaaaa\n'

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.


class OverlayFileWithXFSTest(shared_test_lib.BaseTestCase):
  """Tests the file-like object implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(OverlayFileWithXFSTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['overlay_xfs.dd'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    xfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/upper/c.txt', inode=11088)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/c.txt',
        parent=xfs_path_spec)

    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 9)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      file_object.Open()

  def testSeek(self):
    """Test the seek functionality."""
    xfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/upper/newdir/e.txt', inode=11092)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/newdir/e.txt',
        parent=xfs_path_spec)

    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 28)

    file_object.seek(2)
    self.assertEqual(file_object.read(2), b'is')
    self.assertEqual(file_object.get_offset(), 4)

    file_object.seek(-9, os.SEEK_END)
    self.assertEqual(file_object.read(4), b'over')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEqual(file_object.read(2), b'y!')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(300, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), 300)
    self.assertEqual(file_object.read(2), b'')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

  def testRead(self):
    """Test the read functionality."""
    xfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, parent=self._raw_path_spec,
        location='/lower/a.txt', inode=11079)
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OVERLAY, location='/a.txt',
        parent=xfs_path_spec)
    file_object = overlay_file_io.OverlayFile(self._resolver_context, path_spec)

    file_object.Open()
    read_buffer = file_object.read()

    expected_buffer = b'aaaaaaaa\n'

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.


if __name__ == '__main__':
  unittest.main()
