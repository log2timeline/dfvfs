#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Keramics attribute."""

import unittest

try:
    from pykeramics import vfs as pykeramics_vfs
except ImportError:
    pykeramics_vfs = None

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

try:
    from dfvfs.vfs import keramics_attribute
    from dfvfs.vfs import keramics_file_system
except ImportError:
    pykeramics_vfs = None

from tests import test_lib as shared_test_lib


@unittest.skipIf(pykeramics_vfs is None, "requires pykeramics")
class KeramicsExtendedAttributeTest(shared_test_lib.BaseTestCase):
    """Tests the Keramics extended attribute."""

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

    def testIntialize(self):
        """Tests the __init__ function."""
        path_spec = self.GetPathSpec("/a_directory/a_file")
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

        pykeramics_extended_attribute = (
            file_entry._keramics_file_entry.get_extended_attribute_by_index(0)
        )
        self.assertIsNotNone(pykeramics_extended_attribute)
        self.assertEqual(pykeramics_extended_attribute.name.to_string(), "user.myxattr")

        test_attribute = keramics_attribute.KeramicsExtendedAttribute(
            pykeramics_extended_attribute
        )
        self.assertIsNotNone(test_attribute)

        with self.assertRaises(errors.BackEndError):
            keramics_attribute.KeramicsExtendedAttribute(None)


if __name__ == "__main__":
    unittest.main()
