#!/usr/bin/env python3
"""Tests for the file system implementation using the tarfile."""

import io
import os
import tarfile
import tempfile
import unittest
from unittest import mock

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import tar_file_system

from tests import test_lib as shared_test_lib


class TARFileSystemTest(shared_test_lib.BaseTestCase):
    """Tests the TAR file system."""

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

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenAndClose(self):
        """Test the open and close functionality."""
        file_system = tar_file_system.TARFileSystem(
            self._resolver_context, self._tar_path_spec
        )
        self.assertIsNotNone(file_system)

        file_system.Open()

    def testFileEntryExistsByPathSpec(self):
        """Test the file entry exists by path specification functionality."""
        file_system = tar_file_system.TARFileSystem(
            self._resolver_context, self._tar_path_spec
        )
        self.assertIsNotNone(file_system)

        file_system.Open()

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/bogus", parent=self._os_path_spec
        )
        self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

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

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/folder", parent=test_os_path_spec
        )
        result = file_system.FileEntryExistsByPathSpec(path_spec)
        self.assertTrue(result)

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/folder/syslog",
            parent=test_os_path_spec,
        )
        result = file_system.FileEntryExistsByPathSpec(path_spec)
        self.assertTrue(result)

        # Test on a tar file that has absolute paths.
        test_path = self._GetTestFilePath(["tar", "absolute_paths.tar"])
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

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/folder", parent=test_os_path_spec
        )
        result = file_system.FileEntryExistsByPathSpec(path_spec)
        self.assertTrue(result)

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/folder/syslog",
            parent=test_os_path_spec,
        )
        result = file_system.FileEntryExistsByPathSpec(path_spec)
        self.assertTrue(result)

        # Test on a tar file that has mixed absolute and relative paths.
        test_path = self._GetTestFilePath(["tar", "mixed_paths.tar"])
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

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/folder", parent=test_os_path_spec
        )
        result = file_system.FileEntryExistsByPathSpec(path_spec)
        self.assertTrue(result)

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/folder/syslog",
            parent=test_os_path_spec,
        )
        result = file_system.FileEntryExistsByPathSpec(path_spec)
        self.assertTrue(result)

    def testGetFileEntryByPathSpec(self):
        """Tests the GetFileEntryByPathSpec function."""
        file_system = tar_file_system.TARFileSystem(
            self._resolver_context, self._tar_path_spec
        )
        self.assertIsNotNone(file_system)

        file_system.Open()

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/syslog",
            parent=self._os_path_spec,
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.name, "syslog")

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/bogus", parent=self._os_path_spec
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNone(file_entry)

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

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/folder", parent=test_os_path_spec
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsVirtual())
        self.assertEqual(file_entry.name, "folder")

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/folder/syslog",
            parent=test_os_path_spec,
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.name, "syslog")

        # Test on a tar file that has absolute paths.
        test_path = self._GetTestFilePath(["tar", "absolute_paths.tar"])
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

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/folder", parent=test_os_path_spec
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)
        self.assertTrue(file_entry.IsVirtual())
        self.assertEqual(file_entry.name, "folder")

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location="/folder/syslog",
            parent=test_os_path_spec,
        )
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.name, "syslog")

    def testGetRootFileEntry(self):
        """Test the get root file entry functionality."""
        file_system = tar_file_system.TARFileSystem(
            self._resolver_context, self._tar_path_spec
        )
        self.assertIsNotNone(file_system)

        file_system.Open()

        file_entry = file_system.GetRootFileEntry()

        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.name, "")


class TARFileSystemIndexTest(shared_test_lib.BaseTestCase):
    """Tests the member and directory indexes of the TAR file system."""

    # Members with a leading separator, a missing parent directory, a duplicate
    # name and a directory that is also implied by a file below it.
    _MEMBERS = [
        ("a/", True),
        ("a/b.txt", False),
        ("a/sub/c.txt", False),
        ("a/b.txt", False),
        ("/lead/d.txt", False),
        ("e.txt", False),
        ("virtual/deep/f.txt", False),
    ]

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        # pylint: disable=consider-using-with
        self._resolver_context = context.Context()

        self._temp_directory = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        test_path = os.path.join(self._temp_directory.name, "test.tar")

        with tarfile.open(test_path, mode="w:") as tar_file:
            for index, (name, is_directory) in enumerate(self._MEMBERS):
                tar_info = tarfile.TarInfo(name)
                if is_directory:
                    tar_info.type = tarfile.DIRTYPE
                    tar_file.addfile(tar_info)
                else:
                    data = f"data {index:d}".encode("ascii")
                    tar_info.size = len(data)
                    tar_file.addfile(tar_info, io.BytesIO(data))

        os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._tar_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR, location="/", parent=os_path_spec
        )

        self._file_system = tar_file_system.TARFileSystem(
            self._resolver_context, self._tar_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()
        self._temp_directory.cleanup()

    def _GetNames(self, location):
        """Retrieves the names of the entries of a directory."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TAR,
            location=location,
            parent=self._tar_path_spec.parent,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        return [sub_file_entry.name for sub_file_entry in file_entry.sub_file_entries]

    def testLookupDoesNotScanMembers(self):
        """Tests that lookups and listings do not use tarfile.getmember."""
        with mock.patch.object(
            tarfile.TarFile, "getmember", side_effect=AssertionError("scan")
        ):
            self.assertEqual(self._GetNames("/"), ["a", "e.txt", "virtual"])
            self.assertEqual(self._GetNames("/a"), ["b.txt", "sub", "b.txt"])
            self.assertEqual(self._GetNames("/a/"), ["b.txt", "sub", "b.txt"])
            self.assertEqual(self._GetNames("/a/sub"), ["c.txt"])
            self.assertEqual(self._GetNames("/virtual"), ["deep"])

            path_spec = path_spec_factory.Factory.NewPathSpec(
                definitions.TYPE_INDICATOR_TAR,
                location="/a/b.txt",
                parent=self._tar_path_spec.parent,
            )
            self.assertTrue(self._file_system.FileEntryExistsByPathSpec(path_spec))
            file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
            self.assertIsNotNone(file_entry)
            self.assertIsNotNone(file_entry.GetTARInfo())

    def testDuplicateMemberUsesLastOccurrence(self):
        """Tests that a member that occurs more than once resolves to the last."""
        tar_file = self._file_system.GetTARFile()

        tar_info = self._file_system.GetTARInfoByName("a/b.txt")
        self.assertIs(tar_info, tar_file.getmember("a/b.txt"))
        self.assertIs(tar_info, tar_file.getmembers()[3])

        self.assertIs(
            self._file_system.GetTARInfoByName("a/"), tar_file.getmember("a/")
        )
        self.assertIsNone(self._file_system.GetTARInfoByName("missing"))

    def testGetDirectoryEntryLocations(self):
        """Tests the GetDirectoryEntryLocations function."""
        self.assertEqual(
            self._file_system.GetDirectoryEntryLocations("/virtual/deep"),
            ["/virtual/deep/f.txt"],
        )
        self.assertEqual(self._file_system.GetDirectoryEntryLocations("/none"), [])


if __name__ == "__main__":
    unittest.main()
