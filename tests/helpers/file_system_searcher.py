#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file system searcher."""

import os
import unittest

from dfvfs.lib import definitions
from dfvfs.helpers import fake_file_system_builder
from dfvfs.helpers import file_system_searcher
from dfvfs.path import fake_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import os_file_system
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class FindSpecTest(shared_test_lib.BaseTestCase):
  """Tests for the find specification."""

  # pylint: disable=protected-access

  def _CreateTestFileSystem(self):
    """Create a file system for testing.

    Returns:
      FakeFileSystem: file system for testing.
    """
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()

    test_path = u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py'
    test_file_data = b'\n'.join([
        b'# -*- coding: utf-8 -*-',
        b'"""Digital Forensics Virtual File System (dfVFS).',
        b'',
        b'dfVFS, or Digital Forensics Virtual File System, is a Python module',
        b'that provides read-only access to file-system objects from various',
        b'storage media types and file formats.',
        b'"""'])

    file_system_builder.AddFile(test_path, test_file_data)

    return file_system_builder.file_system

  def testInitialize(self):
    """Test the __init__ function."""
    find_spec = file_system_searcher.FindSpec(location=u'location')
    self.assertIsNotNone(find_spec)

    find_spec = file_system_searcher.FindSpec(location=[u'location'])
    self.assertIsNotNone(find_spec)

    with self.assertRaises(TypeError):
      find_spec = file_system_searcher.FindSpec(location={})

    find_spec = file_system_searcher.FindSpec(location_glob=u'loca?ion')
    self.assertIsNotNone(find_spec)

    find_spec = file_system_searcher.FindSpec(location_glob=[u'loca?ion'])
    self.assertIsNotNone(find_spec)

    with self.assertRaises(TypeError):
      find_spec = file_system_searcher.FindSpec(location_glob={})

    find_spec = file_system_searcher.FindSpec(location_regex=u'loca.ion')
    self.assertIsNotNone(find_spec)

    find_spec = file_system_searcher.FindSpec(location_regex=[u'loca.ion'])
    self.assertIsNotNone(find_spec)

    with self.assertRaises(TypeError):
      find_spec = file_system_searcher.FindSpec(location_regex={})

    with self.assertRaises(ValueError):
      find_spec = file_system_searcher.FindSpec(
          location=u'location', location_glob=u'loca?ion')

  def testCheckFileEntryType(self):
    """Test the _CheckFileEntryType() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckFileEntryType(file_entry)
    self.assertTrue(result)

    file_entry = file_system.GetRootFileEntry()

    result = find_spec._CheckFileEntryType(file_entry)
    self.assertFalse(result)

    find_spec = file_system_searcher.FindSpec()

    result = find_spec._CheckFileEntryType(file_entry)
    self.assertIsNone(result)

  def testCheckIsAllocated(self):
    """Test the _CheckIsAllocated() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsAllocated(file_entry)
    self.assertTrue(result)

  def testCheckIsDevice(self):
    """Test the _CheckIsDevice() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsDevice(file_entry)
    self.assertFalse(result)

  def testCheckIsDirectory(self):
    """Test the _CheckIsDirectory() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsDirectory(file_entry)
    self.assertFalse(result)

  def testCheckIsFile(self):
    """Test the _CheckIsFile() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsFile(file_entry)
    self.assertTrue(result)

  def testCheckIsLink(self):
    """Test the _CheckIsLink() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsLink(file_entry)
    self.assertFalse(result)

  def testCheckIsPipe(self):
    """Test the _CheckIsPipe() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsPipe(file_entry)
    self.assertFalse(result)

  def testCheckIsSocket(self):
    """Test the _CheckIsSocket() function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsSocket(file_entry)
    self.assertFalse(result)

  def testCheckLocation(self):
    """Test the _CheckLocation() function."""
    file_system = self._CreateTestFileSystem()

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    find_spec = file_system_searcher.FindSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    find_spec.PrepareMatches(file_system)

    result = find_spec._CheckLocation(file_entry, 6)
    self.assertTrue(result)

    result = find_spec._CheckLocation(file_entry, 0)
    self.assertTrue(result)

    result = find_spec._CheckLocation(file_entry, 5)
    self.assertFalse(result)

    find_spec = file_system_searcher.FindSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/bogus.py')
    find_spec.PrepareMatches(file_system)

    result = find_spec._CheckLocation(file_entry, 6)
    self.assertFalse(result)

  def testConvertLocationGlob2Regex(self):
    """Test the _ConvertLocationGlob2Regex function."""
    find_spec = file_system_searcher.FindSpec()

    location_regex = find_spec._ConvertLocationGlob2Regex(
        u'/tmp/loca?ion')
    self.assertEqual(location_regex, u'/tmp/loca.ion')

  def testSplitPath(self):
    """Test the _SplitPath function."""
    find_spec = file_system_searcher.FindSpec()

    path_segments = find_spec._SplitPath(u'/tmp/location', u'/')
    self.assertEqual(path_segments, [u'tmp', u'location'])

  # TODO: add tests for AtMaximumDepth

  def testMatches(self):
    """Test the Matches() function."""
    file_system = self._CreateTestFileSystem()

    path_spec = fake_path_spec.FakePathSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    find_spec = file_system_searcher.FindSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    find_spec.PrepareMatches(file_system)

    result = find_spec.Matches(file_entry, 6)
    self.assertEqual(result, (True, True))

    result = find_spec.Matches(file_entry, 0)
    self.assertEqual(result, (False, True))

    find_spec = file_system_searcher.FindSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/bogus.py')
    find_spec.PrepareMatches(file_system)

    result = find_spec.Matches(file_entry, 6)
    self.assertEqual(result, (False, False))

  def testPrepareMatches(self):
    """Test the PrepareMatches function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        location=u'/usr/lib/python2.7/site-packages/dfvfs/__init__.py')

    self.assertIsNone(find_spec._location_segments)
    self.assertEqual(find_spec._number_of_location_segments, 0)

    find_spec.PrepareMatches(file_system)
    self.assertEqual(find_spec._location_segments, [
        u'usr', u'lib', u'python2.7', u'site-packages', u'dfvfs',
        u'__init__.py'])
    self.assertEqual(find_spec._number_of_location_segments, 6)


@shared_test_lib.skipUnlessHasTestFile([u'password.txt'])
@shared_test_lib.skipUnlessHasTestFile([u'vsstest.qcow2'])
class FileSystemSearcherTest(shared_test_lib.BaseTestCase):
  """Tests for the file system searcher."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    self._os_path = self._GetTestFilePath([])
    self._os_path_spec = os_path_spec.OSPathSpec(location=self._os_path)
    self._os_file_system = os_file_system.OSFileSystem(self._resolver_context)

    # TODO: add RAW volume only test image.

    test_file = self._GetTestFilePath([u'vsstest.qcow2'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/', parent=self._qcow_path_spec)

    self._tsk_file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context)
    self._tsk_file_system.Open(self._tsk_path_spec)

  def testFind(self):
    """Test the Find() function."""
    searcher = file_system_searcher.FileSystemSearcher(
        self._tsk_file_system, self._qcow_path_spec)

    # Find all the file entries of type: FILE_ENTRY_TYPE_FILE.
    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/$AttrDef',
        u'/$BadClus',
        u'/$Bitmap',
        u'/$Boot',
        u'/$Extend/$ObjId',
        u'/$Extend/$Quota',
        u'/$Extend/$Reparse',
        u'/$Extend/$RmMetadata/$Repair',
        u'/$Extend/$RmMetadata/$TxfLog/$Tops',
        u'/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf',
        u'/$Extend/$RmMetadata/$TxfLog/$TxfLogContainer00000000000000000001',
        u'/$Extend/$RmMetadata/$TxfLog/$TxfLogContainer00000000000000000002',
        u'/$LogFile',
        u'/$MFT',
        u'/$MFTMirr',
        u'/$Secure',
        u'/$UpCase',
        u'/$Volume',
        u'/another_file',
        u'/password.txt',
        u'/syslog.gz',
        u'/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}',
        (u'/System Volume Information/{600f0b69-5bdf-11e3-9d6c-005056c00008}'
         u'{3808876b-c176-4e48-b7ae-04046e6cc752}'),
        (u'/System Volume Information/{600f0b6d-5bdf-11e3-9d6c-005056c00008}'
         u'{3808876b-c176-4e48-b7ae-04046e6cc752}')]

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries of type: FILE_ENTRY_TYPE_DIRECTORY.
    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_DIRECTORY])
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/',
        u'/$Extend',
        u'/$Extend/$RmMetadata',
        u'/$Extend/$RmMetadata/$Txf',
        u'/$Extend/$RmMetadata/$TxfLog',
        u'/System Volume Information',
        u'/$OrphanFiles']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries of type: FILE_ENTRY_TYPE_LINK.
    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_LINK])
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = []

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a location.
    find_spec1 = file_system_searcher.FindSpec(
        location=u'/$Extend/$RmMetadata')
    find_spec2 = file_system_searcher.FindSpec(
        location=[u'$Extend', u'$RmMetadata', u'$TxfLog', u'$TxfLog.blf'])
    find_spec3 = file_system_searcher.FindSpec(
        location=u'/PASSWORD.TXT')
    path_spec_generator = searcher.Find(
        find_specs=[find_spec1, find_spec2, find_spec3])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/$Extend/$RmMetadata',
        u'/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a case insensitive location.
    find_spec = file_system_searcher.FindSpec(
        location=u'/PASSWORD.TXT', case_sensitive=False)
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/password.txt']

    locations = []
    first_path_spec = None
    for path_spec in path_spec_generator:
      if not first_path_spec:
        first_path_spec = path_spec
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    test_relative_path = searcher.GetRelativePath(first_path_spec)
    self.assertEqual(test_relative_path, u'/password.txt')

    # Find all the file entries with a location glob.
    find_spec1 = file_system_searcher.FindSpec(
        location_glob=u'/*/$RmMetadata')
    find_spec2 = file_system_searcher.FindSpec(
        location_glob=[u'$Extend', u'$RmMetadata', u'*', u'*.blf'])
    find_spec3 = file_system_searcher.FindSpec(
        location_glob=u'/PASSWORD.TXT')
    path_spec_generator = searcher.Find(
        find_specs=[find_spec1, find_spec2, find_spec3])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/$Extend/$RmMetadata',
        u'/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a location regular expression.
    find_spec1 = file_system_searcher.FindSpec(
        location_regex=r'/.*/\$RmMetadata')
    find_spec2 = file_system_searcher.FindSpec(
        location_regex=[r'\$Extend', r'\$RmMetadata', u'.*', u'.*[.]blf'])
    find_spec3 = file_system_searcher.FindSpec(
        location_regex=u'/PASSWORD.TXT')
    path_spec_generator = searcher.Find(
        find_specs=[find_spec1, find_spec2, find_spec3])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/$Extend/$RmMetadata',
        u'/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a case insensitive location glob.
    find_spec = file_system_searcher.FindSpec(
        location_glob=u'/PASSWORD.TXT', case_sensitive=False)
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/password.txt']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a case insensitive location regular
    # expression.
    find_spec = file_system_searcher.FindSpec(
        location_regex=u'/PASSWORD.TXT', case_sensitive=False)
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        u'/password.txt']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a location glob.
    searcher = file_system_searcher.FileSystemSearcher(
        self._os_file_system, self._os_path_spec)

    location = u'{0:s}syslog.*'.format(os.path.sep)
    find_spec = file_system_searcher.FindSpec(
        location_glob=location, case_sensitive=False)
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = sorted([
        self._GetTestFilePath([u'syslog.aes']),
        self._GetTestFilePath([u'syslog.base16']),
        self._GetTestFilePath([u'syslog.base32']),
        self._GetTestFilePath([u'syslog.base64']),
        self._GetTestFilePath([u'syslog.bin.cpio']),
        self._GetTestFilePath([u'syslog.blowfish']),
        self._GetTestFilePath([u'syslog.bz2']),
        self._GetTestFilePath([u'syslog.crc.cpio']),
        self._GetTestFilePath([u'syslog.db']),
        self._GetTestFilePath([u'syslog.des3']),
        self._GetTestFilePath([u'syslog.gz']),
        self._GetTestFilePath([u'syslog.newc.cpio']),
        self._GetTestFilePath([u'syslog.lzma']),
        self._GetTestFilePath([u'syslog.odc.cpio']),
        self._GetTestFilePath([u'syslog.rc4']),
        self._GetTestFilePath([u'syslog.tar']),
        self._GetTestFilePath([u'syslog.tgz']),
        self._GetTestFilePath([u'syslog.xz']),
        self._GetTestFilePath([u'syslog.Z']),
        self._GetTestFilePath([u'syslog.zip']),
        self._GetTestFilePath([u'syslog.zlib'])])

    locations = []
    first_path_spec = None
    for path_spec in path_spec_generator:
      if not first_path_spec:
        first_path_spec = path_spec
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(sorted(locations), expected_locations)

    _, path_separator, relative_path = locations[0].rpartition(os.path.sep)
    expected_relative_path = u'{0:s}{1:s}'.format(
        path_separator, relative_path)
    test_relative_path = searcher.GetRelativePath(first_path_spec)
    self.assertEqual(test_relative_path, expected_relative_path)

    # Find all the file entries with a location regular expression.
    searcher = file_system_searcher.FileSystemSearcher(
        self._os_file_system, self._os_path_spec)

    if os.path.sep == u'\\':
      location = u'\\\\syslog[.].*'
    else:
      location = u'{0:s}syslog[.].*'.format(os.path.sep)

    find_spec = file_system_searcher.FindSpec(
        location_regex=location, case_sensitive=False)
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = sorted([
        self._GetTestFilePath([u'syslog.aes']),
        self._GetTestFilePath([u'syslog.base16']),
        self._GetTestFilePath([u'syslog.base32']),
        self._GetTestFilePath([u'syslog.base64']),
        self._GetTestFilePath([u'syslog.bin.cpio']),
        self._GetTestFilePath([u'syslog.blowfish']),
        self._GetTestFilePath([u'syslog.bz2']),
        self._GetTestFilePath([u'syslog.crc.cpio']),
        self._GetTestFilePath([u'syslog.db']),
        self._GetTestFilePath([u'syslog.des3']),
        self._GetTestFilePath([u'syslog.gz']),
        self._GetTestFilePath([u'syslog.newc.cpio']),
        self._GetTestFilePath([u'syslog.lzma']),
        self._GetTestFilePath([u'syslog.odc.cpio']),
        self._GetTestFilePath([u'syslog.rc4']),
        self._GetTestFilePath([u'syslog.tar']),
        self._GetTestFilePath([u'syslog.tgz']),
        self._GetTestFilePath([u'syslog.xz']),
        self._GetTestFilePath([u'syslog.Z']),
        self._GetTestFilePath([u'syslog.zip']),
        self._GetTestFilePath([u'syslog.zlib'])])

    locations = []
    first_path_spec = None
    for path_spec in path_spec_generator:
      if not first_path_spec:
        first_path_spec = path_spec
      locations.append(getattr(path_spec, u'location', u''))

    self.assertEqual(sorted(locations), expected_locations)

    _, path_separator, relative_path = locations[0].rpartition(os.path.sep)
    expected_relative_path = u'{0:s}{1:s}'.format(
        path_separator, relative_path)
    test_relative_path = searcher.GetRelativePath(first_path_spec)
    self.assertEqual(test_relative_path, expected_relative_path)


if __name__ == '__main__':
  unittest.main()
