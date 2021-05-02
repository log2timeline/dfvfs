#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvshadow."""

import os
import unittest

from dfvfs.file_io import vshadow_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


class VShadowFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the Volume Shadow Snapshots (VSS) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['vss.raw'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClose(self):
    """Test the open and close functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=1)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 82771968)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=13)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      file_object.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss1',
        parent=self._raw_path_spec)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 82771968)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss0',
        parent=self._raw_path_spec)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      file_object.Open()

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, location='/vss13',
        parent=self._raw_path_spec)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      file_object.Open()

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=1)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 82771968)

    file_object.seek(0x1c9)
    self.assertEqual(file_object.get_offset(), 0x1c9)
    self.assertEqual(file_object.read(16), b'rl+Alt+Del to re')
    self.assertEqual(file_object.get_offset(), 473)

    file_object.seek(-40, os.SEEK_END)
    self.assertEqual(file_object.get_offset(), 82771928)
    self.assertEqual(file_object.read(8), b'estart\r\n')
    self.assertEqual(file_object.get_offset(), 82771936)

    file_object.seek(3, os.SEEK_CUR)
    self.assertEqual(file_object.get_offset(), 82771939)
    self.assertEqual(file_object.read(7), b'\x00\x00\x00\x00\x00\x00\x00')
    self.assertEqual(file_object.get_offset(), 82771946)

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    expected_offset = 82771968 + 100
    file_object.seek(expected_offset, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), expected_offset)
    self.assertEqual(file_object.read(20), b'')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), expected_offset)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), expected_offset)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=self._raw_path_spec,
        store_index=1)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context, path_spec)

    file_object.Open()
    self.assertEqual(file_object.get_size(), 82771968)

    file_object.seek(0x18e)

    expected_data = b'disk read error occurred\x00\r\nBOOTMGR is compresse'
    self.assertEqual(file_object.read(47), expected_data)


if __name__ == '__main__':
  unittest.main()
