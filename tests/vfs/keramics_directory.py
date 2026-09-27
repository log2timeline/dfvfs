#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the directory implementation using pykeramics."""

import unittest

try:
    from pykeramics import vfs as pykeramics_vfs
except ImportError:
    pykeramics_vfs = None

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

try:
    from dfvfs.vfs import keramics_directory
    from dfvfs.vfs import keramics_file_system
except ImportError:
    pykeramics_vfs = None

from tests import test_lib as shared_test_lib


@unittest.skipIf(pykeramics_vfs is None, "requires pykeramics")
class KeramicsDirectoryTest(shared_test_lib.BaseTestCase):
    """Tests the Keramics directory."""

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
        keramics_file_entry = self._file_system.GetKeramicsFileEntryByPathSpec(
            path_spec
        )
        directory = keramics_directory.KeramicsDirectory(
            self._file_system, path_spec, keramics_file_entry
        )
        self.assertIsNotNone(directory)

    def testEntriesGenerator(self):
        """Tests the _EntriesGenerator function."""
        path_spec = self.GetPathSpec("/")
        keramics_file_entry = self._file_system.GetKeramicsFileEntryByPathSpec(
            path_spec
        )
        directory = keramics_directory.KeramicsDirectory(
            self._file_system, path_spec, keramics_file_entry
        )
        self.assertIsNotNone(directory)

        entries = list(directory.entries)
        self.assertEqual(len(entries), 4)


if __name__ == "__main__":
    unittest.main()
