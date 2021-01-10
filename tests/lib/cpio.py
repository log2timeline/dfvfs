#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for Copy in and out (CPIO) archive file."""

import unittest

from dfvfs.lib import cpio
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

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

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testReadFileEntryOnBinary(self):
    """Tests the _ReadFileEntry function on binary format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'bin-little-endian'

    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    file_entry = test_file._ReadFileEntry(file_object, 0)
    self.assertEqual(file_entry.data_size, 1247)

  def testReadFileEntryOnNewASCII(self):
    """Tests the _ReadFileEntry function on new ASCII format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'newc'

    test_path = self._GetTestFilePath(['syslog.newc.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    file_entry = test_file._ReadFileEntry(file_object, 0)
    self.assertEqual(file_entry.data_size, 1247)

  def testReadFileEntryOnNewASCIIWithCRC(self):
    """Tests the _ReadFileEntry function on new ASCII with CRC format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'crc'

    test_path = self._GetTestFilePath(['syslog.crc.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    file_entry = test_file._ReadFileEntry(file_object, 0)
    self.assertEqual(file_entry.data_size, 1247)

  def testReadFileEntryOnPortableASCII(self):
    """Tests the _ReadFileEntry function on portable ASCII format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'odc'

    test_path = self._GetTestFilePath(['syslog.odc.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    file_entry = test_file._ReadFileEntry(file_object, 0)
    self.assertEqual(file_entry.data_size, 1247)

  def testReadFileEntriesOnBinary(self):
    """Tests the _ReadFileEntries function on binary format."""
    test_file = cpio.CPIOArchiveFile()
    test_file.file_format = 'bin-little-endian'

    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file._file_size = file_object.get_size()
    test_file._ReadFileEntries(file_object)
    self.assertEqual(len(test_file._file_entries), 1)

  def testFileEntryExistsByPathOnBinary(self):
    """Tests the FileEntryExistsByPath function on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file.Open(file_object)

    result = test_file.FileEntryExistsByPath('syslog')
    self.assertTrue(result)

    result = test_file.FileEntryExistsByPath('bogus')
    self.assertFalse(result)

    test_file.Close()

  def testGetFileEntriesOnBinary(self):
    """Tests the GetFileEntries function on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file.Open(file_object)

    file_entries = list(test_file.GetFileEntries())
    self.assertEqual(len(file_entries), 1)

    test_file.Close()

    file_entries = list(test_file.GetFileEntries())
    self.assertEqual(len(file_entries), 0)

  def testGetFileEntryByPathOnBinary(self):
    """Tests the GetFileEntryByPath function on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file.Open(file_object)

    file_entry = test_file.GetFileEntryByPath('syslog')
    self.assertIsNotNone(file_entry)

    file_entry = test_file.GetFileEntryByPath('bogus')
    self.assertIsNone(file_entry)

    test_file.Close()

  # TODO: add tests for FileEntryExistsByPath
  # TODO: add tests for GetFileEntries
  # TODO: add tests for GetFileEntryByPath

  def testOpenAndCloseOnBinary(self):
    """Tests the Open and Close functions on binary format."""
    test_file = cpio.CPIOArchiveFile()

    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file.Open(file_object)

    self.assertEqual(test_file.file_format, 'bin-little-endian')

    test_file.Close()

  def testOpenAndCloseOnNewASCII(self):
    """Tests the Open and Close functions on new ASCII format."""
    test_file = cpio.CPIOArchiveFile()

    test_path = self._GetTestFilePath(['syslog.newc.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file.Open(file_object)

    self.assertEqual(test_file.file_format, 'newc')

    test_file.Close()

  def testOpenAndCloseOnNewASCIIWithCRC(self):
    """Tests the Open and Close functions on new ASCII with CRC format."""
    test_file = cpio.CPIOArchiveFile()

    test_path = self._GetTestFilePath(['syslog.crc.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file.Open(file_object)

    self.assertEqual(test_file.file_format, 'crc')

    test_file.Close()

  def testOpenAndCloseOnPortableASCII(self):
    """Tests the Open and Close functions on portable ASCII format."""
    test_file = cpio.CPIOArchiveFile()

    test_path = self._GetTestFilePath(['syslog.odc.cpio'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    test_file.Open(file_object)

    self.assertEqual(test_file.file_format, 'odc')

    test_file.Close()

  # TODO: add tests for ReadDataAtOffset


if __name__ == '__main__':
  unittest.main()
