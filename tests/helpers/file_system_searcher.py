#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system searcher."""

from __future__ import unicode_literals

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

    test_path = '/usr/lib/python2.7/site-packages/dfvfs/__init__.py'
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
    find_spec = file_system_searcher.FindSpec(
        location='location', location_separator='/')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['location'])

    find_spec = file_system_searcher.FindSpec(
        location='/location', location_separator='/')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['location'])

    find_spec = file_system_searcher.FindSpec(
        location='\\location', location_separator='\\')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['location'])

    find_spec = file_system_searcher.FindSpec(location=['location'])
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['location'])

    find_spec = file_system_searcher.FindSpec(
        location_glob='loca?ion', location_separator='/')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    find_spec = file_system_searcher.FindSpec(
        location_glob='/loca?ion', location_separator='/')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    find_spec = file_system_searcher.FindSpec(
        location_glob='\\loca?ion', location_separator='\\')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    find_spec = file_system_searcher.FindSpec(location_glob=['loca?ion'])
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    find_spec = file_system_searcher.FindSpec(
        location_regex='loca.ion', location_separator='/')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    find_spec = file_system_searcher.FindSpec(
        location_regex='/loca.ion', location_separator='/')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    find_spec = file_system_searcher.FindSpec(
        location_regex='\\\\loca.ion', location_separator='\\')
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    find_spec = file_system_searcher.FindSpec(location_regex=['loca.ion'])
    self.assertIsNotNone(find_spec)
    self.assertEqual(find_spec._location_segments, ['loca.ion'])

    with self.assertRaises(ValueError):
      find_spec = file_system_searcher.FindSpec(
          location='location', location_glob='loca?ion')

    with self.assertRaises(ValueError):
      find_spec = file_system_searcher.FindSpec(
          location='location', location_separator=None)

    with self.assertRaises(TypeError):
      find_spec = file_system_searcher.FindSpec(location={})

    with self.assertRaises(TypeError):
      find_spec = file_system_searcher.FindSpec(location_glob={})

    with self.assertRaises(TypeError):
      find_spec = file_system_searcher.FindSpec(location_regex={})

  def testCheckFileEntryType(self):
    """Test the _CheckFileEntryType function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
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
    """Test the _CheckIsAllocated function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsAllocated(file_entry)
    self.assertTrue(result)

  def testCheckIsDevice(self):
    """Test the _CheckIsDevice function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsDevice(file_entry)
    self.assertFalse(result)

  def testCheckIsDirectory(self):
    """Test the _CheckIsDirectory function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsDirectory(file_entry)
    self.assertFalse(result)

  def testCheckIsFile(self):
    """Test the _CheckIsFile function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsFile(file_entry)
    self.assertTrue(result)

  def testCheckIsLink(self):
    """Test the _CheckIsLink function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsLink(file_entry)
    self.assertFalse(result)

  def testCheckIsPipe(self):
    """Test the _CheckIsPipe function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsPipe(file_entry)
    self.assertFalse(result)

  def testCheckIsSocket(self):
    """Test the _CheckIsSocket function."""
    file_system = self._CreateTestFileSystem()

    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    result = find_spec._CheckIsSocket(file_entry)
    self.assertFalse(result)

  def testCompareWithLocationSegment(self):
    """Test the _CompareWithLocationSegment function."""
    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec._CompareWithLocationSegment('__init__.py', 6)
    self.assertTrue(result)

    result = find_spec._CompareWithLocationSegment('__init__.py', 0)
    self.assertTrue(result)

    result = find_spec._CompareWithLocationSegment('__init__.py', 5)
    self.assertFalse(result)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/bogus.py',
        location_separator='/')

    result = find_spec._CompareWithLocationSegment('__init__.py', 6)
    self.assertFalse(result)

  def testConvertLocationGlob2Regex(self):
    """Test the _ConvertLocationGlob2Regex function."""
    find_spec = file_system_searcher.FindSpec()

    location_regex = find_spec._ConvertLocationGlob2Regex(
        '/tmp/loca?ion')
    self.assertEqual(location_regex, '/tmp/loca.ion')

  def testSplitPath(self):
    """Test the _SplitPath function."""
    find_spec = file_system_searcher.FindSpec()

    path_segments = find_spec._SplitPath('/tmp/location', '/')
    self.assertEqual(path_segments, ['tmp', 'location'])

  def testAtLastLocationSegment(self):
    """Test the AtLastLocationSegment function."""
    find_spec = file_system_searcher.FindSpec()

    result = find_spec.AtLastLocationSegment(6)
    self.assertFalse(result)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.AtLastLocationSegment(0)
    self.assertFalse(result)

    result = find_spec.AtLastLocationSegment(6)
    self.assertTrue(result)

    result = find_spec.AtLastLocationSegment(9)
    self.assertTrue(result)

  def testAtMaximumDepth(self):
    """Test the AtMaximumDepth function."""
    find_spec = file_system_searcher.FindSpec()

    result = find_spec.AtMaximumDepth(6)
    self.assertFalse(result)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.AtMaximumDepth(0)
    self.assertFalse(result)

    result = find_spec.AtMaximumDepth(6)
    self.assertTrue(result)

    result = find_spec.AtMaximumDepth(9)
    self.assertTrue(result)

  def testCompareLocation(self):
    """Test the CompareLocation function."""
    file_system = self._CreateTestFileSystem()

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.CompareLocation(file_entry)
    self.assertTrue(result)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/bogus.py',
        location_separator='/')

    result = find_spec.CompareLocation(file_entry)
    self.assertFalse(result)

  def testCompareNameWithLocationSegment(self):
    """Test the CompareNameWithLocationSegment function."""
    file_system = self._CreateTestFileSystem()

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.CompareNameWithLocationSegment(file_entry, 6)
    self.assertTrue(result)

    result = find_spec.CompareNameWithLocationSegment(file_entry, 5)
    self.assertFalse(result)

    # Currently comparing against the root location segment always
    # returns True.
    result = find_spec.CompareNameWithLocationSegment(file_entry, 0)
    self.assertTrue(result)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/bogus.py',
        location_separator='/')

    result = find_spec.CompareNameWithLocationSegment(file_entry, 6)
    self.assertFalse(result)

  def testCompareTraits(self):
    """Test the CompareTraits function."""
    file_system = self._CreateTestFileSystem()

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.CompareTraits(file_entry)
    self.assertTrue(result)

  def testHasLocation(self):
    """Test the HasLocation function."""
    find_spec = file_system_searcher.FindSpec()

    result = find_spec.HasLocation()
    self.assertFalse(result)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.HasLocation()
    self.assertTrue(result)

  def testIsLastLocationSegment(self):
    """Test the IsLastLocationSegment function."""
    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.IsLastLocationSegment(0)
    self.assertFalse(result)

    result = find_spec.IsLastLocationSegment(6)
    self.assertTrue(result)

    result = find_spec.IsLastLocationSegment(9)
    self.assertFalse(result)

  def testMatches(self):
    """Test the Matches function."""
    file_system = self._CreateTestFileSystem()

    path_spec = fake_path_spec.FakePathSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py')
    file_entry = file_system.GetFileEntryByPathSpec(path_spec)

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/__init__.py',
        location_separator='/')

    result = find_spec.Matches(file_entry)
    self.assertEqual(result, (True, True))

    result = find_spec.Matches(file_entry, search_depth=6)
    self.assertEqual(result, (True, True))

    result = find_spec.Matches(file_entry, search_depth=0)
    self.assertEqual(result, (False, True))

    find_spec = file_system_searcher.FindSpec(
        location='/usr/lib/python2.7/site-packages/dfvfs/bogus.py',
        location_separator='/')

    result = find_spec.Matches(file_entry, search_depth=6)
    self.assertEqual(result, (False, False))


class FileSystemSearcherTest(shared_test_lib.BaseTestCase):
  """Tests for the file system searcher."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath([])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._os_file_system = os_file_system.OSFileSystem(self._resolver_context)

    # TODO: add RAW volume only test image.

    test_file = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)
    self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
        location='/', parent=self._qcow_path_spec)

    self._tsk_file_system = tsk_file_system.TSKFileSystem(
        self._resolver_context)
    self._tsk_file_system.Open(self._tsk_path_spec)

  def testFind(self):
    """Test the Find function."""
    searcher = file_system_searcher.FileSystemSearcher(
        self._tsk_file_system, self._qcow_path_spec)

    # Find all the file entries of type: FILE_ENTRY_TYPE_FILE.
    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_FILE])
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/$AttrDef',
        '/$BadClus',
        '/$Bitmap',
        '/$Boot',
        '/$Extend/$ObjId',
        '/$Extend/$Quota',
        '/$Extend/$Reparse',
        '/$Extend/$RmMetadata/$Repair',
        '/$Extend/$RmMetadata/$TxfLog/$Tops',
        '/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf',
        '/$Extend/$RmMetadata/$TxfLog/$TxfLogContainer00000000000000000001',
        '/$Extend/$RmMetadata/$TxfLog/$TxfLogContainer00000000000000000002',
        '/$LogFile',
        '/$MFT',
        '/$MFTMirr',
        '/$Secure',
        '/$UpCase',
        '/$Volume',
        '/another_file',
        '/password.txt',
        '/syslog.gz',
        '/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}',
        ('/System Volume Information/{600f0b69-5bdf-11e3-9d6c-005056c00008}'
         '{3808876b-c176-4e48-b7ae-04046e6cc752}'),
        ('/System Volume Information/{600f0b6d-5bdf-11e3-9d6c-005056c00008}'
         '{3808876b-c176-4e48-b7ae-04046e6cc752}')]

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries of type: FILE_ENTRY_TYPE_DIRECTORY.
    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_DIRECTORY])
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/',
        '/$Extend',
        '/$Extend/$RmMetadata',
        '/$Extend/$RmMetadata/$Txf',
        '/$Extend/$RmMetadata/$TxfLog',
        '/System Volume Information']

    locations = []
    for path_spec in path_spec_generator:
      # Some versions of Sleuthkit include "/$OrphanFiles" some don't.
      location = getattr(path_spec, 'location', '')
      if location != '/$OrphanFiles':
        locations.append(location)

    self.assertEqual(locations, expected_locations)

    # Find all the file entries of type: FILE_ENTRY_TYPE_LINK.
    find_spec = file_system_searcher.FindSpec(
        file_entry_types=[definitions.FILE_ENTRY_TYPE_LINK])
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = []

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a location.
    find_spec1 = file_system_searcher.FindSpec(
        location='/$Extend/$RmMetadata',
        location_separator='/')
    find_spec2 = file_system_searcher.FindSpec(
        location=['$Extend', '$RmMetadata', '$TxfLog', '$TxfLog.blf'])
    find_spec3 = file_system_searcher.FindSpec(
        location='/PASSWORD.TXT',
        location_separator='/')
    path_spec_generator = searcher.Find(
        find_specs=[find_spec1, find_spec2, find_spec3])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/$Extend/$RmMetadata',
        '/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a case insensitive location.
    find_spec = file_system_searcher.FindSpec(
        case_sensitive=False, location='/PASSWORD.TXT', location_separator='/')
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/password.txt']

    locations = []
    first_path_spec = None
    for path_spec in path_spec_generator:
      if not first_path_spec:
        first_path_spec = path_spec
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    test_relative_path = searcher.GetRelativePath(first_path_spec)
    self.assertEqual(test_relative_path, '/password.txt')

    # Find all the file entries with a location glob.
    find_spec1 = file_system_searcher.FindSpec(
        location_glob='/*/$RmMetadata', location_separator='/')
    find_spec2 = file_system_searcher.FindSpec(
        location_glob=['$Extend', '$RmMetadata', '*', '*.blf'])
    find_spec3 = file_system_searcher.FindSpec(
        location_glob='/PASSWORD.TXT', location_separator='/')
    path_spec_generator = searcher.Find(
        find_specs=[find_spec1, find_spec2, find_spec3])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/$Extend/$RmMetadata',
        '/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a location regular expression.
    find_spec1 = file_system_searcher.FindSpec(
        location_regex=r'/.*/\$RmMetadata', location_separator='/')
    find_spec2 = file_system_searcher.FindSpec(
        location_regex=[r'\$Extend', r'\$RmMetadata', '.*', '.*[.]blf'])
    find_spec3 = file_system_searcher.FindSpec(
        location_regex='/PASSWORD.TXT', location_separator='/')
    path_spec_generator = searcher.Find(
        find_specs=[find_spec1, find_spec2, find_spec3])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/$Extend/$RmMetadata',
        '/$Extend/$RmMetadata/$TxfLog/$TxfLog.blf']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a case insensitive location glob.
    find_spec = file_system_searcher.FindSpec(
        case_sensitive=False, location_glob='/PASSWORD.TXT',
        location_separator='/')
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/password.txt']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a case insensitive location regular
    # expression.
    find_spec = file_system_searcher.FindSpec(
        case_sensitive=False, location_regex='/PASSWORD.TXT',
        location_separator='/')
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = [
        '/password.txt']

    locations = []
    for path_spec in path_spec_generator:
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(locations, expected_locations)

    # Find all the file entries with a location glob.
    searcher = file_system_searcher.FileSystemSearcher(
        self._os_file_system, self._os_path_spec)

    location = '{0:s}syslog.*'.format(os.path.sep)
    find_spec = file_system_searcher.FindSpec(
        case_sensitive=False, location_glob=location,
        location_separator=os.path.sep)
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = sorted([
        self._GetTestFilePath(['syslog.aes']),
        self._GetTestFilePath(['syslog.base16']),
        self._GetTestFilePath(['syslog.base32']),
        self._GetTestFilePath(['syslog.base64']),
        self._GetTestFilePath(['syslog.bin.cpio']),
        self._GetTestFilePath(['syslog.blowfish']),
        self._GetTestFilePath(['syslog.bz2']),
        self._GetTestFilePath(['syslog.crc.cpio']),
        self._GetTestFilePath(['syslog.db']),
        self._GetTestFilePath(['syslog.des3']),
        self._GetTestFilePath(['syslog.gz']),
        self._GetTestFilePath(['syslog.newc.cpio']),
        self._GetTestFilePath(['syslog.lzma']),
        self._GetTestFilePath(['syslog.odc.cpio']),
        self._GetTestFilePath(['syslog.rc4']),
        self._GetTestFilePath(['syslog.tar']),
        self._GetTestFilePath(['syslog.tgz']),
        self._GetTestFilePath(['syslog.xz']),
        self._GetTestFilePath(['syslog.Z']),
        self._GetTestFilePath(['syslog.zip']),
        self._GetTestFilePath(['syslog.zlib'])])

    locations = []
    first_path_spec = None
    for path_spec in path_spec_generator:
      if not first_path_spec:
        first_path_spec = path_spec
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(sorted(locations), expected_locations)

    _, path_separator, relative_path = locations[0].rpartition(os.path.sep)
    expected_relative_path = '{0:s}{1:s}'.format(
        path_separator, relative_path)
    test_relative_path = searcher.GetRelativePath(first_path_spec)
    self.assertEqual(test_relative_path, expected_relative_path)

    # Find all the file entries with a location regular expression.
    searcher = file_system_searcher.FileSystemSearcher(
        self._os_file_system, self._os_path_spec)

    if os.path.sep == '\\':
      location = '\\\\syslog[.].*'
    else:
      location = '{0:s}syslog[.].*'.format(os.path.sep)

    find_spec = file_system_searcher.FindSpec(
        case_sensitive=False, location_regex=location,
        location_separator=os.path.sep)
    path_spec_generator = searcher.Find(find_specs=[find_spec])
    self.assertIsNotNone(path_spec_generator)

    expected_locations = sorted([
        self._GetTestFilePath(['syslog.aes']),
        self._GetTestFilePath(['syslog.base16']),
        self._GetTestFilePath(['syslog.base32']),
        self._GetTestFilePath(['syslog.base64']),
        self._GetTestFilePath(['syslog.bin.cpio']),
        self._GetTestFilePath(['syslog.blowfish']),
        self._GetTestFilePath(['syslog.bz2']),
        self._GetTestFilePath(['syslog.crc.cpio']),
        self._GetTestFilePath(['syslog.db']),
        self._GetTestFilePath(['syslog.des3']),
        self._GetTestFilePath(['syslog.gz']),
        self._GetTestFilePath(['syslog.newc.cpio']),
        self._GetTestFilePath(['syslog.lzma']),
        self._GetTestFilePath(['syslog.odc.cpio']),
        self._GetTestFilePath(['syslog.rc4']),
        self._GetTestFilePath(['syslog.tar']),
        self._GetTestFilePath(['syslog.tgz']),
        self._GetTestFilePath(['syslog.xz']),
        self._GetTestFilePath(['syslog.Z']),
        self._GetTestFilePath(['syslog.zip']),
        self._GetTestFilePath(['syslog.zlib'])])

    locations = []
    first_path_spec = None
    for path_spec in path_spec_generator:
      if not first_path_spec:
        first_path_spec = path_spec
      locations.append(getattr(path_spec, 'location', ''))

    self.assertEqual(sorted(locations), expected_locations)

    _, path_separator, relative_path = locations[0].rpartition(os.path.sep)
    expected_relative_path = '{0:s}{1:s}'.format(
        path_separator, relative_path)
    test_relative_path = searcher.GetRelativePath(first_path_spec)
    self.assertEqual(test_relative_path, expected_relative_path)


if __name__ == '__main__':
  unittest.main()
