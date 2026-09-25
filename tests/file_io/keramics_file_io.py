#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Keramics file-like object."""

import os
import unittest

try:
    from pykeramics import vfs as pykeramics_vfs
except ImportError:
    pykeramics_vfs = None

from dfvfs.file_io import keramics_file_io
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


@unittest.skipIf(pykeramics_vfs is None, "requires pykeramics")
class KeramcisFileTest(shared_test_lib.BaseTestCase):
    """Tests the file-like object implementation using pyfsext.file_entry."""

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
        super().setUp()
        self._resolver_context = context.Context()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenCloseLocation(self):
        """Test the open and close functionality using a location."""
        path_spec = self.GetPathSpec("/passwords.txt")
        file_object = keramics_file_io.KeramicsFile(self._resolver_context, path_spec)

        file_object.Open()
        self.assertEqual(file_object.get_size(), 116)

    def testSeek(self):
        """Test the seek functionality."""
        path_spec = self.GetPathSpec("/a_directory/another_file")
        file_object = keramics_file_io.KeramicsFile(self._resolver_context, path_spec)

        file_object.Open()
        self.assertEqual(file_object.get_size(), 22)

        file_object.seek(10)
        self.assertEqual(file_object.read(5), b"other")
        self.assertEqual(file_object.get_offset(), 15)

        file_object.seek(-10, os.SEEK_END)
        self.assertEqual(file_object.read(5), b"her f")

        file_object.seek(2, os.SEEK_CUR)
        self.assertEqual(file_object.read(2), b"e.")

        # Conforming to the POSIX seek the offset can exceed the file size
        # but reading will result in no data being returned.
        file_object.seek(300, os.SEEK_SET)
        self.assertEqual(file_object.get_offset(), 300)
        self.assertEqual(file_object.read(2), b"")

        with self.assertRaises(IOError):
            file_object.seek(-10, os.SEEK_SET)

        # On error the offset should not change.
        self.assertEqual(file_object.get_offset(), 300)

        with self.assertRaises(IOError):
            file_object.seek(10, 5)

        # On error the offset should not change.
        self.assertEqual(file_object.get_offset(), 300)

    def testRead(self):
        """Test the read functionality."""
        path_spec = self.GetPathSpec("/passwords.txt")
        file_object = keramics_file_io.KeramicsFile(self._resolver_context, path_spec)

        file_object.Open()
        read_buffer = file_object.read()

        expected_buffer = (
            b"place,user,password\n"
            b"bank,joesmith,superrich\n"
            b"alarm system,-,1234\n"
            b"treasure chest,-,1111\n"
            b"uber secret laire,admin,admin\n"
        )

        self.assertEqual(read_buffer, expected_buffer)

        # TODO: add boundary scenarios.


if __name__ == "__main__":
    unittest.main()
