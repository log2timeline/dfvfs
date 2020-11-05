#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvshadow."""

from __future__ import unicode_literals

import os
import unittest

from dfvfs.lib import errors
from dfvfs.file_io import vshadow_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


class VShadowFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the Volume Shadow Snapshots (VSS) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClose(self):
    """Test the open and close functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 0x40000000)
    file_object.close()

    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=13)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/vss1', parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 0x40000000)
    file_object.close()

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/vss0', parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location='/vss13', parent=self._qcow_path_spec)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 0x40000000)

    file_object.seek(0x1e0)
    self.assertEqual(file_object.get_offset(), 0x1e0)
    self.assertEqual(file_object.read(16), b'rl+Alt+Del to re')
    self.assertEqual(file_object.get_offset(), 0x1f0)

    file_object.seek(-40, os.SEEK_END)
    self.assertEqual(file_object.get_offset(), 0x3fffffd8)
    self.assertEqual(file_object.read(8), b'Press Ct')
    self.assertEqual(file_object.get_offset(), 0x3fffffe0)

    file_object.seek(3, os.SEEK_CUR)
    self.assertEqual(file_object.get_offset(), 0x3fffffe3)
    self.assertEqual(file_object.read(7), b'Alt+Del')
    self.assertEqual(file_object.get_offset(), 0x3fffffea)

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    expected_offset = 0x40000000 + 100
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

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        parent=self._qcow_path_spec, store_index=1)
    file_object = vshadow_file_io.VShadowFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 0x40000000)

    file_object.seek(0x18e)

    expected_data = b'A disk read error occurred\x00\r\nBOOTMGR is missing'
    self.assertEqual(file_object.read(47), expected_data)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
