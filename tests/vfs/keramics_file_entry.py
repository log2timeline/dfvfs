#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using pyfsext."""

import unittest

try:
    from pykeramics import vfs as pykeramics_vfs
except ImportError:
    pykeramics_vfs = None

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import keramics_attribute
from dfvfs.vfs import keramics_file_entry
from dfvfs.vfs import keramics_file_system

from tests import test_lib as shared_test_lib


@unittest.skipIf(pykeramics_vfs is None, "requires pykeramics")
class KeramicsFileEntryTestWithEXT2(shared_test_lib.BaseTestCase):
    """Tests the Keramics file entry on an ext2 image."""

    # pylint: disable=protected-access

    def GetPathSpec(self, path):
        """Retrieves a path specification of the test file.

        Args:
          path (str): path of the test file within the test image.

        Returns:
          PathSpec: path specification of the test file.
        """
        image_path = self._GetTestFilePath(["ext2.raw"])
        self._SkipIfPathNotExists(image_path)

        os_location = pykeramics_vfs.VfsLocation.new_base_from_string(
            pykeramics_vfs.VfsType.OS, image_path
        )
        ext_location = os_location.new_with_layer_from_string(
            pykeramics_vfs.VfsType.EXT, path
        )
        return path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_KERAMICS, location=ext_location
        )

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()

        path_spec = self.GetPathSpec("/")
        self._file_system = keramics_file_system.KeramicsFileSystem(
            self._resolver_context, path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testInitialize(self):
        """Tests the __init__ function."""
        path_spec = self.GetPathSpec("/")
        pykeramics_file_entry = self._file_system.GetKeramicsFileEntryByPathSpec(
            path_spec
        )
        test_file_entry = keramics_file_entry.KeramicsFileEntry(
            self._resolver_context,
            self._file_system,
            path_spec,
            pykeramics_file_entry=pykeramics_file_entry,
        )
        self.assertIsNotNone(test_file_entry)

    def testAccessTime(self):
        """Test the access_time property."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(test_file_entry)
        self.assertIsNotNone(test_file_entry.access_time)

    def testChangeTime(self):
        """Test the change_time property."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(test_file_entry)
        self.assertIsNotNone(test_file_entry.change_time)

    def testCreationTime(self):
        """Test the creation_time property."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(test_file_entry)
        self.assertIsNone(test_file_entry.creation_time)

    def testModificationTime(self):
        """Test the modification_time property."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(test_file_entry)
        self.assertIsNotNone(test_file_entry.modification_time)

    def testGetAttributes(self):
        """Tests the _GetAttributes function."""
        path_spec = self.GetPathSpec("/a_directory/a_file")
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        self.assertIsNone(file_entry._attributes)

        file_entry._GetAttributes()
        self.assertIsNotNone(file_entry._attributes)
        self.assertEqual(len(file_entry._attributes), 2)

        test_attribute = file_entry._attributes[0]
        self.assertIsInstance(
            test_attribute, keramics_attribute.KeramicsExtendedAttribute
        )
        self.assertEqual(test_attribute.name, "user.myxattr")

        test_attribute_value_data = test_attribute.read()
        self.assertEqual(test_attribute_value_data, b"My extended attribute")

    def testGetStatAttribute(self):
        """Tests the _GetStatAttribute function."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        stat_attribute = test_file_entry._GetStatAttribute()

        self.assertIsNotNone(stat_attribute)
        self.assertIsNone(stat_attribute.device_number)
        self.assertEqual(stat_attribute.group_identifier, 1000)
        self.assertEqual(stat_attribute.inode_number, 15)
        self.assertEqual(stat_attribute.mode, 0o100664)
        self.assertEqual(stat_attribute.number_of_links, 1)
        self.assertEqual(stat_attribute.owner_identifier, 1000)
        self.assertEqual(stat_attribute.size, 22)
        self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

    def testGetExtents(self):
        """Tests the GetExtents function."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        extents = test_file_entry.GetExtents()
        # TODO: add support for extents
        self.assertEqual(len(extents), 0)

    def testGetFileEntryByPathSpec(self):
        """Tests the GetFileEntryByPathSpec function."""
        path_spec = self.GetPathSpec("/a_directory/a_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(test_file_entry)

    def testGetLinkedFileEntry(self):
        """Tests the GetLinkedFileEntry function."""
        path_spec = self.GetPathSpec("/a_link")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        linked_file_entry = test_file_entry.GetLinkedFileEntry()

        self.assertIsNotNone(linked_file_entry)

        self.assertEqual(linked_file_entry.name, "another_file")

    def testGetParentFileEntry(self):
        """Tests the GetParentFileEntry function."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        parent_file_entry = test_file_entry.GetParentFileEntry()

        self.assertIsNotNone(parent_file_entry)

        self.assertEqual(parent_file_entry.name, "a_directory")

    def testIsFunctions(self):
        """Tests the Is* functions."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        self.assertFalse(test_file_entry.IsRoot())
        self.assertFalse(test_file_entry.IsVirtual())
        self.assertTrue(test_file_entry.IsAllocated())

        self.assertFalse(test_file_entry.IsDevice())
        self.assertFalse(test_file_entry.IsDirectory())
        self.assertTrue(test_file_entry.IsFile())
        self.assertFalse(test_file_entry.IsLink())
        self.assertFalse(test_file_entry.IsPipe())
        self.assertFalse(test_file_entry.IsSocket())

        path_spec = self.GetPathSpec("/a_directory")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        self.assertFalse(test_file_entry.IsRoot())
        self.assertFalse(test_file_entry.IsVirtual())
        self.assertTrue(test_file_entry.IsAllocated())

        self.assertFalse(test_file_entry.IsDevice())
        self.assertTrue(test_file_entry.IsDirectory())
        self.assertFalse(test_file_entry.IsFile())
        self.assertFalse(test_file_entry.IsLink())
        self.assertFalse(test_file_entry.IsPipe())
        self.assertFalse(test_file_entry.IsSocket())

        path_spec = self.GetPathSpec("/")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        self.assertTrue(test_file_entry.IsRoot())
        self.assertFalse(test_file_entry.IsVirtual())
        self.assertTrue(test_file_entry.IsAllocated())

        self.assertFalse(test_file_entry.IsDevice())
        self.assertTrue(test_file_entry.IsDirectory())
        self.assertFalse(test_file_entry.IsFile())
        self.assertFalse(test_file_entry.IsLink())
        self.assertFalse(test_file_entry.IsPipe())
        self.assertFalse(test_file_entry.IsSocket())

    def testSubFileEntries(self):
        """Tests the number_of_sub_file_entries and sub_file_entries properties."""
        path_spec = self.GetPathSpec("/")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        self.assertEqual(test_file_entry.number_of_sub_file_entries, 4)

        expected_sub_file_entry_names = [
            "a_directory",
            "a_link",
            "lost+found",
            "passwords.txt",
        ]
        sub_file_entry_names = []

        for sub_file_entry in test_file_entry.sub_file_entries:
            sub_file_entry_names.append(sub_file_entry.name)

        self.assertEqual(len(sub_file_entry_names), len(expected_sub_file_entry_names))
        self.assertEqual(
            sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names)
        )

    def testDataStreams(self):
        """Tests the data streams functionality."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        self.assertEqual(test_file_entry.number_of_data_streams, 1)

        data_stream_names = []
        for data_stream in test_file_entry.data_streams:
            data_stream_names.append(data_stream.name)

        self.assertEqual(data_stream_names, [""])

        path_spec = self.GetPathSpec("/a_directory")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        self.assertEqual(test_file_entry.number_of_data_streams, 0)

        data_stream_names = []
        for data_stream in test_file_entry.data_streams:
            data_stream_names.append(data_stream.name)

        self.assertEqual(data_stream_names, [])

    def testGetDataStream(self):
        """Tests the GetDataStream function."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        test_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(test_file_entry)

        data_stream_name = ""
        data_stream = test_file_entry.GetDataStream(data_stream_name)
        self.assertIsNotNone(data_stream)


if __name__ == "__main__":
    unittest.main()
