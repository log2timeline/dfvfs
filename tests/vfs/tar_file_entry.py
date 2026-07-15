#!/usr/bin/env python3
"""Tests for the file entry implementation using the tarfile."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import tar_file_entry
from dfvfs.vfs import tar_file_system

from tests import test_lib as shared_test_lib


class TARFileEntryTest(shared_test_lib.BaseTestCase):
    """Tests the TAR extracted file entry."""

    # pylint: disable=protected-access

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["tar", "syslog.tar"])
        self._SkipIfPathNotExists(test_path)

        self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._tar_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        self._file_system = tar_file_system.TARFileSystem(
            self._resolver_context, self._tar_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testIntialize(self):
        """Test the __init__ function."""
        file_entry = tar_file_entry.TARFileEntry(
            self._resolver_context, self._file_system, self._tar_path_spec
        )
        self.assertIsNotNone(file_entry)

    # TODO: add tests for _GetDirectory
    # TODO: add tests for _GetLink

    def testGetStatAttribute(self):
        """Tests the _GetStatAttribute function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        stat_attribute = file_entry._GetStatAttribute()

        self.assertIsNotNone(stat_attribute)
        self.assertEqual(stat_attribute.group_identifier, 5000)
        self.assertEqual(stat_attribute.mode, 0o400)
        self.assertEqual(stat_attribute.owner_identifier, 151107)
        self.assertEqual(stat_attribute.size, 1247)
        self.assertEqual(stat_attribute.type, stat_attribute.TYPE_FILE)

    # TODO: add tests for _GetSubFileEntries

    def testModificationTime(self):
        """Test the modification_time property."""
        file_entry = tar_file_entry.TARFileEntry(
            self._resolver_context, self._file_system, self._tar_path_spec
        )
        self.assertIsNotNone(file_entry)
        self.assertIsNotNone(file_entry.modification_time)

    def testName(self):
        """Test the name property."""
        file_entry = tar_file_entry.TARFileEntry(
            self._resolver_context, self._file_system, self._tar_path_spec
        )
        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.name, "syslog")

    def testSize(self):
        """Test the size property."""
        file_entry = tar_file_entry.TARFileEntry(
            self._resolver_context, self._file_system, self._tar_path_spec
        )
        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.size, 1247)

    def testGetParentFileEntry(self):
        """Tests the GetParentFileEntry function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        parent_file_entry = file_entry.GetParentFileEntry()
        self.assertIsNotNone(parent_file_entry)
        self.assertEqual(parent_file_entry.name, "")

    # TODO: add tests for GetTARInfo

    def testIsAllocated(self):
        """Test the IsAllocated function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsAllocated())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsAllocated())

    def testIsDevice(self):
        """Test the IsDevice function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsDevice())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsDevice())

    def testIsDirectory(self):
        """Test the IsDirectory function."""
        # Test with an in-file directory.
        test_path = self._GetTestFilePath(["tar", "with_directory.tar"])
        self._SkipIfPathNotExists(test_path)

        os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        tar_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=os_path_spec
        )
        file_system = tar_file_system.TARFileSystem(
            self._resolver_context, tar_path_spec
        )
        file_system.Open()

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/folder", parent=os_path_spec
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsDirectory())
        self.assertFalse(file_entry.IsVirtual())

        # Test with a virtual directory.
        test_path = self._GetTestFilePath(["tar", "without_directory.tar"])
        self._SkipIfPathNotExists(test_path)

        os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        tar_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=os_path_spec
        )
        file_system = tar_file_system.TARFileSystem(
            self._resolver_context, tar_path_spec
        )
        file_system.Open()

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/folder", parent=os_path_spec
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsDirectory())
        self.assertTrue(file_entry.IsVirtual())

    def testIsFile(self):
        """Test the IsFile function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsFile())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsFile())

    def testIsLink(self):
        """Test the IsLink function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsLink())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsLink())

    def testIsPipe(self):
        """Test the IsPipe function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsPipe())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsPipe())

    def testIsRoot(self):
        """Test the IsRoot function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsRoot())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsRoot())

    def testIsSocket(self):
        """Test the IsSocket function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsSocket())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsSocket())

    def testIsVirtual(self):
        """Test the IsVirtual function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertFalse(file_entry.IsVirtual())

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsVirtual())

    def testSubFileEntries(self):
        """Test the sub file entries iteration functionality."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        self._assertSubFileEntries(file_entry, ["syslog"])

        # Test on a tar file without directories.
        test_path = self._GetTestFilePath(["tar", "without_directory.tar"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=test_os_path_spec
        )
        file_system = tar_file_system.TARFileSystem(self._resolver_context, path_spec)
        self.assertIsNotNone(file_system)

        file_system.Open()

        file_entry = file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        self._assertSubFileEntries(file_entry, ["folder"])

        # The "folder" folder is a missing directory entry but should still be found
        # due to the files found inside the directory.
        sub_file_entry = next(file_entry.sub_file_entries)
        self.assertTrue(sub_file_entry.IsVirtual())
        self._assertSubFileEntries(sub_file_entry, ["syslog", "wtmp.1"])

    def testDataStreams(self):
        """Test the data streams functionality."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        self.assertEqual(file_entry.number_of_data_streams, 1)

        data_stream_names = []
        for data_stream in file_entry.data_streams:
            data_stream_names.append(data_stream.name)

        self.assertEqual(data_stream_names, [""])

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=self._os_path_spec
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        self.assertEqual(file_entry.number_of_data_streams, 0)

        data_stream_names = []
        for data_stream in file_entry.data_streams:
            data_stream_names.append(data_stream.name)

        self.assertEqual(data_stream_names, [])

    def testGetDataStream(self):
        """Tests the GetDataStream function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        data_stream_name = ""
        data_stream = file_entry.GetDataStream(data_stream_name)
        self.assertIsNotNone(data_stream)
        self.assertEqual(data_stream.name, data_stream_name)

        data_stream = file_entry.GetDataStream("bogus")
        self.assertIsNone(data_stream)


if __name__ == "__main__":
    unittest.main()
