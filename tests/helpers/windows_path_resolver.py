#!/usr/bin/env python3
"""Tests for the Windows path resolver object."""

import unittest

from dfvfs.helpers import fake_file_system_builder
from dfvfs.helpers import windows_path_resolver
from dfvfs.path import fake_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_entry
from dfvfs.vfs import os_file_system
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class WindowsPathResolverTest(shared_test_lib.BaseTestCase):
    """The unit test for the windows path resolver object."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()

        test_file = self._GetTestFilePath([])
        self._SkipIfPathNotExists(test_file)

        self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
        self._os_file_system = os_file_system.OSFileSystem(
            self._resolver_context, self._os_path_spec
        )

        # TODO: add RAW volume only test image.

        test_file = self._GetTestFilePath(["vss.raw"])
        self._SkipIfPathNotExists(test_file)

        path_spec = os_path_spec.OSPathSpec(location=test_file)
        self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)
        self._tsk_path_spec = tsk_path_spec.TSKPathSpec(
            location="/", parent=self._raw_path_spec
        )

        self._tsk_file_system = tsk_file_system.TSKFileSystem(
            self._resolver_context, self._tsk_path_spec
        )
        self._tsk_file_system.Open()

    def testResolvePathDirectory(self):
        """Test the resolve path function on a mount point directory."""
        path_resolver = windows_path_resolver.WindowsPathResolver(
            self._os_file_system, self._os_path_spec
        )

        expected_path = self._GetTestFilePath(["testdir_os", "file1.txt"])

        windows_path = "C:\\testdir_os\\file1.txt"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        test_windows_path = path_resolver.GetWindowsPath(path_spec)
        self.assertEqual(test_windows_path, windows_path)

        windows_path = "C:\\testdir_os\\file6.txt"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

    def testResolvePathImage(self):
        """Test the resolve path function on a storage media image."""
        path_resolver = windows_path_resolver.WindowsPathResolver(
            self._tsk_file_system, self._raw_path_spec
        )
        expected_path = (
            "/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}"
        )
        windows_path = (
            "C:\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}"
        )
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        test_windows_path = path_resolver.GetWindowsPath(path_spec)
        self.assertEqual(test_windows_path, windows_path)

        windows_path = (
            "\\\\?\\C:\\System Volume Information"
            "\\{3808876b-c176-4e48-b7ae-04046e6cc752}"
        )
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        windows_path = (
            "\\\\.\\C:\\System Volume Information"
            "\\{3808876b-c176-4e48-b7ae-04046e6cc752}"
        )
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        expected_path = "/passwords.txt"

        windows_path = "\\PASSWORDS.TXT"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        windows_path = "C:\\..\\PASSWORDS.TXT"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        expected_path = "/"

        windows_path = "\\"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        windows_path = "S"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        windows_path = "\\\\?\\"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        windows_path = "\\\\.\\"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        windows_path = "\\\\?\\UNC\\server\\share\\directory\\file.txt"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        windows_path = "\\\\server\\share\\directory\\file.txt"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        windows_path = "SYSLOG.GZ"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        windows_path = ".\\SYSLOG.GZ"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        windows_path = "..\\SYSLOG.GZ"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

    def testResolvePathWithEnvironmentVariable(self):
        """Test the resolve path function with environment variable expansion."""
        path_resolver = windows_path_resolver.WindowsPathResolver(
            self._tsk_file_system, self._raw_path_spec
        )
        path_resolver.SetEnvironmentVariable(
            "SystemRoot", "C:\\System Volume Information"
        )
        expected_path = (
            "/System Volume Information/{3808876b-c176-4e48-b7ae-04046e6cc752}"
        )
        windows_path = "%SystemRoot%\\{3808876b-c176-4e48-b7ae-04046e6cc752}"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

        expected_windows_path = (
            "C:\\System Volume Information\\{3808876b-c176-4e48-b7ae-04046e6cc752}"
        )
        test_windows_path = path_resolver.GetWindowsPath(path_spec)
        self.assertEqual(test_windows_path, expected_windows_path)

        windows_path = "%WinDir%\\{3808876b-c176-4e48-b7ae-04046e6cc752}"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNone(path_spec)

        # Test resolving multi path segment environment variables.
        path_resolver = windows_path_resolver.WindowsPathResolver(
            self._os_file_system, self._os_path_spec
        )
        expected_path = self._GetTestFilePath(["testdir_os", "subdir1", "file6.txt"])

        path_resolver.SetEnvironmentVariable("Test", "C:\\testdir_os\\subdir1")

        windows_path = "%Test%\\file6.txt"
        path_spec = path_resolver.ResolvePath(windows_path)
        self.assertIsNotNone(path_spec)
        self.assertEqual(path_spec.location, expected_path)

    def testResolvePathDirectoryCache(self):
        """Test the resolve path function caches directory listings."""
        # pylint: disable=protected-access
        file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()
        for location in (
            "/Windows/System32/Config/SAM",
            "/Windows/System32/Config/SYSTEM",
            "/Windows/System32/drivers/etc/hosts",
            "/Windows/system32/lower.txt",
            "/WINDOWS/Other.txt",
            "/Users/Test/NTUSER.DAT",
        ):
            file_system_builder.AddFile(location, b"data")

        file_system = file_system_builder.file_system
        mount_point = fake_path_spec.FakePathSpec(location="/")

        windows_paths = [
            "C:\\Windows\\System32\\Config\\SAM",
            "C:\\windows\\SYSTEM32\\config\\sam",
            "C:\\Windows\\system32\\lower.txt",
            "C:\\WINDOWS\\SYSTEM32\\LOWER.TXT",
            "C:\\Windows\\Other.txt",
            "C:\\windows\\other.txt",
            "C:\\WINDOWS\\Other.txt",
            "C:\\Windows\\System32\\Config\\Missing",
            "C:\\Windows\\System32\\..\\System32\\drivers\\ETC\\hosts",
            "C:\\Windows\\.\\System32\\\\Config",
            "C:\\users\\TEST\\ntuser.dat",
            "C:\\Missing\\File",
        ]

        path_resolver = windows_path_resolver.WindowsPathResolver(
            file_system, mount_point
        )
        # The fake file system is a system level file system, for which the
        # cache is disabled by default, but the content is static in this test.
        path_resolver._use_directory_cache = True

        # The reference resolver does not cache and uses the file entry
        # GetSubFileEntryByName function directly.
        reference_resolver = windows_path_resolver.WindowsPathResolver(
            file_system, mount_point
        )
        reference_resolver._use_directory_cache = False

        expected_locations = {}
        for windows_path in windows_paths:
            path_spec = reference_resolver.ResolvePath(windows_path)
            expected_locations[windows_path] = path_spec.location if path_spec else None

        listing_counts = {}
        original_property = fake_file_entry.FakeFileEntry.sub_file_entries

        def _CountingSubFileEntries(file_entry):
            """Counts the listings per directory."""
            location = file_entry.path_spec.location
            listing_counts[location] = listing_counts.get(location, 0) + 1
            return original_property.fget(file_entry)

        fake_file_entry.FakeFileEntry.sub_file_entries = property(
            _CountingSubFileEntries
        )
        try:
            for _ in range(3):
                for windows_path in windows_paths:
                    path_spec = path_resolver.ResolvePath(windows_path)
                    location = path_spec.location if path_spec else None
                    self.assertEqual(
                        location, expected_locations[windows_path], msg=windows_path
                    )
        finally:
            fake_file_entry.FakeFileEntry.sub_file_entries = original_property

        # Each directory is listed once, where without the cache every resolved
        # path segment lists its directory again.
        self.assertIsNotNone(listing_counts)
        for location, count in listing_counts.items():
            self.assertEqual(count, 1, msg=location)


if __name__ == "__main__":
    unittest.main()
