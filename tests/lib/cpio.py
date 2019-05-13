#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for Copy in and out (CPIO) archive file."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import file_object_io
from dfvfs.lib import cpio

from tests import test_lib as shared_test_lib


class CPIOArchiveFileEntryTest(shared_test_lib.BaseTestCase):
  """Tests for Copy in and out (CPIO) archive file entry."""

  def testInitialize(self):
    """Tests the __init__ function."""
    file_entry = cpio.CPIOArchiveFileEntry()
    self.assertIsNotNone(file_entry)


class CPIOArchiveFileTest(shared_test_lib.BaseTestCase):
  """Tests for Copy in and out (CPIO) archive file."""

  # pylint: disable=protected-access

  def testReadFileEntryOnBinary(self):
    """Tests the _ReadFileEntry function on binary format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'bin-little-endian'

    test_file_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      file_entry = test_file._ReadFileEntry(file_io_object, 0)
      self.assertEqual(file_entry.data_size, 1247)

      file_io_object.close()

  def testReadFileEntryOnNewASCII(self):
    """Tests the _ReadFileEntry function on new ASCII format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'newc'

    test_file_path = self._GetTestFilePath(['syslog.newc.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      file_entry = test_file._ReadFileEntry(file_io_object, 0)
      self.assertEqual(file_entry.data_size, 1247)

      file_io_object.close()

  def testReadFileEntryOnNewASCIIWithCRC(self):
    """Tests the _ReadFileEntry function on new ASCII with CRC format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'crc'

    test_file_path = self._GetTestFilePath(['syslog.crc.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      file_entry = test_file._ReadFileEntry(file_io_object, 0)
      self.assertEqual(file_entry.data_size, 1247)

      file_io_object.close()

  def testReadFileEntryOnPortableASCII(self):
    """Tests the _ReadFileEntry function on portable ASCII format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'odc'

    test_file_path = self._GetTestFilePath(['syslog.odc.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      file_entry = test_file._ReadFileEntry(file_io_object, 0)
      self.assertEqual(file_entry.data_size, 1247)

      file_io_object.close()

  def testReadFileEntriesOnBinary(self):
    """Tests the _ReadFileEntries function on binary format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'bin-little-endian'

    test_file_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file._file_size = file_io_object.get_size()
      test_file._ReadFileEntries(file_io_object)
      self.assertEqual(len(test_file._file_entries), 1)

      file_io_object.close()

  def testFileEntryExistsByPathOnBinary(self):
    """Tests the FileEntryExistsByPath function on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_file_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file.Open(file_io_object)

      result = test_file.FileEntryExistsByPath('syslog')
      self.assertTrue(result)

      result = test_file.FileEntryExistsByPath('bogus')
      self.assertFalse(result)

      test_file.Close()
      file_io_object.close()

  def testGetFileEntriesOnBinary(self):
    """Tests the GetFileEntries function on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_file_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file.Open(file_io_object)

      file_entries = list(test_file.GetFileEntries())
      self.assertEqual(len(file_entries), 1)

      test_file.Close()

      file_entries = list(test_file.GetFileEntries())
      self.assertEqual(len(file_entries), 0)

      file_io_object.close()

  def testGetFileEntryByPathOnBinary(self):
    """Tests the GetFileEntryByPath function on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_file_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file.Open(file_io_object)

      file_entry = test_file.GetFileEntryByPath('syslog')
      self.assertIsNotNone(file_entry)

      file_entry = test_file.GetFileEntryByPath('bogus')
      self.assertIsNone(file_entry)

      test_file.Close()
      file_io_object.close()

  # TODO: add tests for FileEntryExistsByPath
  # TODO: add tests for GetFileEntries
  # TODO: add tests for GetFileEntryByPath

  def testOpenAndCloseOnBinary(self):
    """Tests the Open and Close functions on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_file_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file.Open(file_io_object)

      self.assertEqual(test_file.file_format, 'bin-little-endian')

      test_file.Close()
      file_io_object.close()

  def testOpenAndCloseOnNewASCII(self):
    """Tests the Open and Close functions on new ASCII format."""
    test_file = cpio.CPIOArchiveFile()

    test_file_path = self._GetTestFilePath(['syslog.newc.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file.Open(file_io_object)

      self.assertEqual(test_file.file_format, 'newc')

      test_file.Close()
      file_io_object.close()

  def testOpenAndCloseOnNewASCIIWithCRC(self):
    """Tests the Open and Close functions on new ASCII with CRC format."""
    test_file = cpio.CPIOArchiveFile()

    test_file_path = self._GetTestFilePath(['syslog.crc.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file.Open(file_io_object)

      self.assertEqual(test_file.file_format, 'crc')

      test_file.Close()
      file_io_object.close()

  def testOpenAndCloseOnPortableASCII(self):
    """Tests the Open and Close functions on portable ASCII format."""
    test_file = cpio.CPIOArchiveFile()

    test_file_path = self._GetTestFilePath(['syslog.odc.cpio'])
    self._SkipIfPathNotExists(test_file_path)

    with open(test_file_path, 'rb') as file_object:
      file_io_object = file_object_io.FileObjectIO(
          None, file_object=file_object)
      file_io_object.open()

      test_file.Open(file_io_object)

      self.assertEqual(test_file.file_format, 'odc')

      test_file.Close()
      file_io_object.close()

  # TODO: add tests for ReadDataAtOffset


if __name__ == '__main__':
  unittest.main()
