#!/usr/bin/env python3
"""Tests for the directory implementation using the CPIOArchiveFile."""

import unittest
from unittest import mock

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import cpio_directory
from dfvfs.vfs import cpio_file_system

from tests import test_lib as shared_test_lib


class CPIODirectoryTest(shared_test_lib.BaseTestCase):
    """Tests the CPIO directory."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["syslog.bin.cpio"])
        self._SkipIfPathNotExists(test_path)

        self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._cpio_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_CPIO,
            location="/syslog",
            parent=self._os_path_spec,
        )

        self._file_system = cpio_file_system.CPIOFileSystem(
            self._resolver_context, self._cpio_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testInitialize(self):
        """Tests the __init__ function."""
        directory = cpio_directory.CPIODirectory(
            self._file_system, self._cpio_path_spec
        )

        self.assertIsNotNone(directory)

    def testEntriesGenerator(self):
        """Tests the _EntriesGenerator function."""
        directory = cpio_directory.CPIODirectory(
            self._file_system, self._cpio_path_spec
        )

        self.assertIsNotNone(directory)

        entries = list(directory.entries)
        self.assertEqual(len(entries), 1)


class CPIODirectoryIndexTest(shared_test_lib.BaseTestCase):
    """Tests the directory entry index of the CPIO file system."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["syslog.bin.cpio"])
        self._SkipIfPathNotExists(test_path)

        os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._cpio_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_CPIO, location="/", parent=os_path_spec
        )

        self._file_system = cpio_file_system.CPIOFileSystem(
            self._resolver_context, self._cpio_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testEntriesGeneratorUsesIndex(self):
        """Tests that listing a directory does not scan the archive entries."""
        archive_file = self._file_system.GetCPIOArchiveFile()
        expected_paths = [
            f"/{file_entry.path:s}" for file_entry in archive_file.GetFileEntries()
        ]
        self.assertEqual(expected_paths, ["/syslog"])

        directory = cpio_directory.CPIODirectory(
            self._file_system, self._cpio_path_spec
        )

        with mock.patch.object(
            type(archive_file),
            "GetFileEntries",
            side_effect=AssertionError("scan"),
        ):
            locations = [entry.location for entry in directory.entries]

        self.assertEqual(locations, expected_paths)

    def testDirectoryEntryLocations(self):
        """Tests the GetDirectoryEntryLocations function with nested paths."""
        file_entries = {
            path: mock.Mock(path=path)
            for path in ("a/b.txt", "a/c.txt", "f/g/d.txt", "e.txt")
        }
        archive_file = self._file_system.GetCPIOArchiveFile()

        with mock.patch.object(
            type(archive_file),
            "GetFileEntries",
            return_value=list(file_entries.values()),
        ):
            self._file_system._BuildDirectoryEntries()  # pylint: disable=protected-access

        self.assertEqual(
            self._file_system.GetDirectoryEntryLocations("/"), ["/a", "/f", "/e.txt"]
        )
        self.assertEqual(
            self._file_system.GetDirectoryEntryLocations("/a/"),
            ["/a/b.txt", "/a/c.txt"],
        )
        self.assertEqual(
            self._file_system.GetDirectoryEntryLocations("/f/g"), ["/f/g/d.txt"]
        )
        self.assertEqual(self._file_system.GetDirectoryEntryLocations("/none"), [])


if __name__ == "__main__":
    unittest.main()
