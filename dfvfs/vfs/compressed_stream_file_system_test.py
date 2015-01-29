#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the compressed stream file system implementation."""

import os
import unittest

from dfvfs.file_io import os_file_io
from dfvfs.lib import definitions
from dfvfs.path import compressed_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import compressed_stream_file_system


class CompressedStreamFileSystemTest(unittest.TestCase):
  """The unit test for the compressed stream file system object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join('test_data', 'syslog.bz2')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._os_file_object = os_file_io.OSFile(self._resolver_context)
    self._os_file_object.open(self._os_path_spec, mode='rb')

  def testIntialize(self):
    """Test the intialize functionality."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context, definitions.COMPRESSION_METHOD_BZIP2,
        self._os_path_spec)

    self.assertNotEquals(file_system, None)

  def testFileEntryExistsByPathSpec(self):
    """Test the file entry exists by path specification functionality."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context, definitions.COMPRESSION_METHOD_BZIP2,
        self._os_path_spec)

    path_spec = compressed_stream_path_spec.CompressedStreamPathSpec(
        compression_method=definitions.COMPRESSION_METHOD_BZIP2,
        parent=self._os_path_spec)

    self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

  def testGetFileEntryByPathSpec(self):
    """Test the get entry by path specification functionality."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context, definitions.COMPRESSION_METHOD_BZIP2,
        self._os_path_spec)

    path_spec = compressed_stream_path_spec.CompressedStreamPathSpec(
        compression_method=definitions.COMPRESSION_METHOD_BZIP2,
        parent=self._os_path_spec)
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')

  def testGetRootFileEntry(self):
    """Test the get root file entry functionality."""
    file_system = compressed_stream_file_system.CompressedStreamFileSystem(
        self._resolver_context, definitions.COMPRESSION_METHOD_BZIP2,
        self._os_path_spec)

    file_entry = file_system.GetRootFileEntry()

    self.assertNotEquals(file_entry, None)
    self.assertEquals(file_entry.name, u'')


if __name__ == '__main__':
  unittest.main()
