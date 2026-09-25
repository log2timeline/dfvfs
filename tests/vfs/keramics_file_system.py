#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file system implementation using pyfsext."""

import unittest

try:
    from pykeramics import vfs as pykeramics_vfs
except ImportError:
    pykeramics_vfs = None

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import keramics_file_system

from tests import test_lib as shared_test_lib


@unittest.skipIf(pykeramics_vfs is None, "requires pykeramics")
class KeramicsFileSystemTest(shared_test_lib.BaseTestCase):
    """Tests the Keramics file entry."""

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

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenAndClose(self):
        """Test the open and close functionality."""
        path_spec = self.GetPathSpec("/")
        file_system = keramics_file_system.KeramicsFileSystem(
            self._resolver_context, path_spec
        )
        self.assertIsNotNone(file_system)

        file_system.Open()

    def testFileEntryExistsByPathSpec(self):
        """Test the file entry exists by path specification functionality."""
        path_spec = self.GetPathSpec("/")
        file_system = keramics_file_system.KeramicsFileSystem(
            self._resolver_context, path_spec
        )
        self.assertIsNotNone(file_system)

        file_system.Open()

        path_spec = self.GetPathSpec("/passwords.txt")
        self.assertTrue(file_system.FileEntryExistsByPathSpec(path_spec))

        path_spec = self.GetPathSpec("/bogus.txt")
        self.assertFalse(file_system.FileEntryExistsByPathSpec(path_spec))

    def testGetFileEntryByPathSpec(self):
        """Tests the GetFileEntryByPathSpec function."""
        path_spec = self.GetPathSpec("/")
        file_system = keramics_file_system.KeramicsFileSystem(
            self._resolver_context, path_spec
        )
        file_system.Open()

        path_spec = self.GetPathSpec("/passwords.txt")
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.name, "passwords.txt")

        path_spec = self.GetPathSpec("/bogus.txt")
        file_entry = file_system.GetFileEntryByPathSpec(path_spec)

        self.assertIsNone(file_entry)

    def testGetRootFileEntry(self):
        """Test the get root file entry functionality."""
        path_spec = self.GetPathSpec("/")
        file_system = keramics_file_system.KeramicsFileSystem(
            self._resolver_context, path_spec
        )
        self.assertIsNotNone(file_system)

        file_system.Open()

        file_entry = file_system.GetRootFileEntry()

        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry.name, "")


if __name__ == "__main__":
    unittest.main()
