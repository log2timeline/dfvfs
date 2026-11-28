#!/usr/bin/env python3
"""Tests for the file-like object implementation using pyvmdk."""

import hashlib
import os
import shutil
import tempfile
import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class VMDKFileTest(test_lib.Ext2ImageFileTestCase):
    """Tests the VMDK image file-like object."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        super().setUp()
        test_path = self._GetTestFilePath(["ext2.vmdk"])
        self._SkipIfPathNotExists(test_path)

        self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._vmdk_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_VMDK, parent=self._os_path_spec
        )

    def testOpenCloseInode(self):
        """Test the open and close functionality using an inode."""
        self._TestOpenCloseInode(self._vmdk_path_spec)

    def testOpenCloseLocation(self):
        """Test the open and close functionality using a location."""
        self._TestOpenCloseLocation(self._vmdk_path_spec)

        # Try open with a path specification that has no parent.
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_VMDK, parent=self._os_path_spec
        )
        path_spec.parent = None

        with self.assertRaises(errors.PathSpecError):
            self._TestOpenCloseLocation(path_spec)

    def testSeek(self):
        """Test the seek functionality."""
        self._TestSeek(self._vmdk_path_spec)

    def testRead(self):
        """Test the read functionality."""
        self._TestRead(self._vmdk_path_spec)


class VMDKDifferentialFileTest(test_lib.Ext2ImageFileTestCase):
    """Tests the VMDK image file-like object with a parent image.

    The test file ext2-differential.vmdk is a monolithicSparse differential image of
    which ext2.vmdk is the parent image. It contains an additional file
    /a_directory/new_file. It was created in the test_data directory with qemu-img
    and qemu-io 10.0.13 (Debian 1:10.0.13+ds-0+deb13u1) and debugfs 1.47.2, using
    the following commands, which utils/generate_test_data_linux.sh mirrors:

    * qemu-img create -f vmdk -o subformat=monolithicSparse -b ext2.vmdk -F vmdk
      ext2-differential.vmdk
    * cp ext2.raw ext2-differential.raw
    * printf 'This is a file in the differential image.\\n' > new_file
    * printf 'cd a_directory\\nwrite new_file new_file\\n' > commands
    * debugfs -w -f commands ext2-differential.raw
    * for each 64 KiB grain N that differs from ext2.raw (grains 0 and 2):
      dd if=ext2-differential.raw of=grain bs=64k skip=N count=1 and
      qemu-io -f vmdk -c "write -s grain $((N*65536)) 65536" ext2-differential.vmdk
    * qemu-img compare ext2-differential.vmdk ext2-differential.raw
    """

    _DIFFERENTIAL_IMAGE_SHA256 = (
        "ccabcb2dd8eae4c2b3d41dcea118c983af39f2f2ffd0959ff5cad77676fe3bd5"
    )

    _NEW_FILE_DATA = b"This is a file in the differential image.\n"

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        super().setUp()
        self._parent_test_path = self._GetTestFilePath(["ext2.vmdk"])
        self._SkipIfPathNotExists(self._parent_test_path)

        self._test_path = self._GetTestFilePath(["ext2-differential.vmdk"])
        self._SkipIfPathNotExists(self._test_path)

        self._vmdk_path_spec = self._GetVMDKPathSpec(self._test_path)

    def _CopyDifferentialImage(self, temp_directory, replacements=None):
        """Copies the differential image into a temporary directory.

        Args:
          temp_directory (str): path of the temporary directory.
          replacements (Optional[list[tuple[bytes, bytes]]]): data to replace in
              the descriptor, where both values must have the same size.

        Returns:
          str: path of the copy of the differential image.
        """
        with open(self._test_path, "rb") as file_object:
            data = file_object.read()

        for old_data, new_data in replacements or []:
            self.assertEqual(len(old_data), len(new_data))
            self.assertEqual(data.count(old_data), 1)
            data = data.replace(old_data, new_data)

        path = os.path.join(temp_directory, "ext2-differential.vmdk")
        with open(path, "wb") as file_object:
            file_object.write(data)

        return path

    def _GetVMDKPathSpec(self, path):
        """Retrieves a VMDK path specification.

        Args:
          path (str): path of the VMDK image.

        Returns:
          PathSpec: VMDK path specification.
        """
        os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=path
        )
        return path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_VMDK, parent=os_path_spec
        )

    def testOpenCloseLocation(self):
        """Test the open and close functionality using a location."""
        self._TestOpenCloseLocation(self._vmdk_path_spec)

    def testRead(self):
        """Test the read functionality."""
        self._TestRead(self._vmdk_path_spec)

        file_object = resolver.Resolver.OpenFileObject(
            self._vmdk_path_spec, resolver_context=self._resolver_context
        )
        self.assertEqual(file_object.get_size(), 4194304)

        data = file_object.read(4194304)
        self.assertEqual(
            hashlib.sha256(data).hexdigest(), self._DIFFERENTIAL_IMAGE_SHA256
        )

    def testReadNewFile(self):
        """Test reading a file that only exists in the differential image."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.PREFERRED_EXT_BACK_END,
            location="/a_directory",
            parent=self._vmdk_path_spec,
        )
        file_entry = resolver.Resolver.OpenFileEntry(
            path_spec, resolver_context=self._resolver_context
        )
        self.assertIsNotNone(file_entry)
        self._assertSubFileEntries(file_entry, ["a_file", "another_file", "new_file"])

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.PREFERRED_EXT_BACK_END,
            location="/a_directory/new_file",
            parent=self._vmdk_path_spec,
        )
        file_object = resolver.Resolver.OpenFileObject(
            path_spec, resolver_context=self._resolver_context
        )
        self.assertEqual(file_object.read(), self._NEW_FILE_DATA)

    def testOpenWithMissingParent(self):
        """Test opening a differential image without its parent image."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_directory:
            path = self._CopyDifferentialImage(temp_directory)

            with self.assertRaisesRegex(
                errors.BackEndError, "Unable to locate parent image: ext2.vmdk"
            ):
                resolver.Resolver.OpenFileObject(
                    self._GetVMDKPathSpec(path),
                    resolver_context=self._resolver_context,
                )

    def testOpenWithParentFilenameOutsideDirectory(self):
        """Test opening a differential image with a parent filename hint path."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_directory:
            shutil.copyfile(
                self._parent_test_path, os.path.join(temp_directory, "e.vmdk")
            )
            sub_directory = os.path.join(temp_directory, "sub")
            os.mkdir(sub_directory)

            path = self._CopyDifferentialImage(
                sub_directory,
                replacements=[
                    (
                        b'parentFileNameHint="ext2.vmdk"',
                        b'parentFileNameHint="../e.vmdk"',
                    )
                ],
            )

            with self.assertRaisesRegex(
                errors.BackEndError, "Unable to locate parent image: e.vmdk"
            ):
                resolver.Resolver.OpenFileObject(
                    self._GetVMDKPathSpec(path),
                    resolver_context=self._resolver_context,
                )

    def testOpenWithParentContentIdentifierMismatch(self):
        """Test opening a differential image with a mismatching parent image."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_directory:
            shutil.copyfile(
                self._parent_test_path, os.path.join(temp_directory, "ext2.vmdk")
            )
            path = self._CopyDifferentialImage(
                temp_directory,
                replacements=[(b"parentCID=dc80b6c7", b"parentCID=0badc0de")],
            )

            with self.assertRaisesRegex(
                errors.BackEndError,
                "Content identifier of parent image: ext2.vmdk does not match",
            ):
                resolver.Resolver.OpenFileObject(
                    self._GetVMDKPathSpec(path),
                    resolver_context=self._resolver_context,
                )

    def testOpenWithoutParentContentIdentifier(self):
        """Test opening an image with a parent filename but no parent image."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_directory:
            path = self._CopyDifferentialImage(
                temp_directory,
                replacements=[(b"parentCID=dc80b6c7", b"parentCID=ffffffff")],
            )

            file_object = resolver.Resolver.OpenFileObject(
                self._GetVMDKPathSpec(path), resolver_context=self._resolver_context
            )
            self.assertEqual(file_object.get_size(), 4194304)


if __name__ == "__main__":
    unittest.main()
