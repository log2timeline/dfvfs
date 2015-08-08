#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the zipfile."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import zip_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import zip_file_entry
from dfvfs.vfs import zip_file_system


class ZipFileEntryTest(unittest.TestCase):
  """The unit test for the zip extracted file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.zip')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        location=u'/', parent=self._os_path_spec)

    self._file_system = zip_file_system.ZipFileSystem(self._resolver_context)
    self._file_system.Open(path_spec=self._zip_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = zip_file_entry.ZipFileEntry(
        self._resolver_context, self._file_system, self._zip_path_spec)

    self.assertNotEqual(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertNotEqual(parent_file_entry, None)

    self.assertEqual(parent_file_entry.name, u'')

  def testGetStat(self):
    """Test the get stat functionality."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    stat_object = file_entry.GetStat()

    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

    expected_sub_file_entry_names = [u'syslog', u'wtmp.1']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def testDataStreams(self):
    """Test the data streams functionality."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_data_streams, 1)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [u''])

    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_data_streams, 0)

    data_stream_names = []
    for data_stream in file_entry.data_streams:
      data_stream_names.append(data_stream.name)

    self.assertEqual(data_stream_names, [])

  def testGetDataStream(self):
    """Test the retrieve data streams functionality."""
    path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=self._os_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self.assertNotEqual(file_entry, None)

    data_stream_name = u''
    data_stream = file_entry.GetDataStream(data_stream_name)
    self.assertNotEqual(data_stream, None)
    self.assertEqual(data_stream.name, data_stream_name)

    file_object = data_stream.GetFileObject()
    self.assertNotEqual(file_object, None)
    file_object.close()

    data_stream = file_entry.GetDataStream(u'bogus')
    self.assertEqual(data_stream, None)


if __name__ == '__main__':
  unittest.main()
