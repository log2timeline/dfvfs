#!/usr/bin/env python3
"""Tests for the directory implementation using the zipfile."""

import os
import tempfile
import unittest
import zipfile
from unittest import mock

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import zip_directory
from dfvfs.vfs import zip_file_system

from tests import test_lib as shared_test_lib


class ZIPDirectoryTest(shared_test_lib.BaseTestCase):
    """Tests the ZIP extracted file directory."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["zip", "syslog.zip"])
        self._SkipIfPathNotExists(test_path)

        self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._zip_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_ZIP, location="/", parent=self._os_path_spec
        )
        self._file_system = zip_file_system.ZipFileSystem(
            self._resolver_context, self._zip_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testInitialize(self):
        """Tests the __init__ function."""
        directory = zip_directory.ZIPDirectory(self._file_system, self._zip_path_spec)

        self.assertIsNotNone(directory)

    def testEntriesGenerator(self):
        """Tests the _EntriesGenerator function."""
        directory = zip_directory.ZIPDirectory(self._file_system, self._zip_path_spec)

        self.assertIsNotNone(directory)

        entries = list(directory.entries)
        self.assertEqual(len(entries), 2)


class ZIPDirectoryIndexTest(shared_test_lib.BaseTestCase):
    """Tests the directory entry index of the ZIP file system."""

    # Members with a missing parent directory, a leading separator and a
    # directory that occurs more than once.
    _MEMBERS = [
        "a/",
        "a/b.txt",
        "a/sub/c.txt",
        "a/sub/",
        "/lead/d.txt",
        "e.txt",
        "virtual/deep/f.txt",
        "virtual/deep/g.txt",
    ]

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        # pylint: disable=consider-using-with
        self._resolver_context = context.Context()

        self._temp_directory = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        test_path = os.path.join(self._temp_directory.name, "test.zip")

        with zipfile.ZipFile(test_path, "w") as zip_file:
            for name in self._MEMBERS:
                zip_file.writestr(name, b"" if name.endswith("/") else b"data")

        os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._zip_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_ZIP, location="/", parent=os_path_spec
        )

        self._file_system = zip_file_system.ZipFileSystem(
            self._resolver_context, self._zip_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()
        self._temp_directory.cleanup()

    def _GetLocations(self, location):
        """Retrieves the locations of the entries of a directory."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_ZIP,
            location=location,
            parent=self._zip_path_spec.parent,
        )
        directory = zip_directory.ZIPDirectory(self._file_system, path_spec)
        return [entry.location for entry in directory.entries]

    def testEntriesGeneratorUsesIndex(self):
        """Tests that listing a directory does not scan the archive members."""
        with mock.patch.object(
            zipfile.ZipFile, "infolist", side_effect=AssertionError("scan")
        ):
            self.assertEqual(self._GetLocations("/"), ["/a/", "/e.txt", "/virtual/"])
            self.assertEqual(self._GetLocations("/a"), ["/a/b.txt", "/a/sub/"])
            self.assertEqual(self._GetLocations("/a/"), ["/a/b.txt", "/a/sub/"])
            self.assertEqual(self._GetLocations("/a/sub"), ["/a/sub/c.txt"])
            self.assertEqual(self._GetLocations("/virtual"), ["/virtual/deep/"])
            self.assertEqual(
                self._GetLocations("/virtual/deep"),
                ["/virtual/deep/f.txt", "/virtual/deep/g.txt"],
            )
            self.assertEqual(self._GetLocations("/none"), [])


if __name__ == "__main__":
    unittest.main()
