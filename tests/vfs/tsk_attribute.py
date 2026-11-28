#!/usr/bin/env python3
"""Tests for the attribute implementation using pytsk3."""

import unittest

import pytsk3

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.vfs import ntfs_file_system
from dfvfs.vfs import tsk_attribute
from dfvfs.vfs import tsk_file_system

from tests import test_lib as shared_test_lib


class TSKAttributeTest(shared_test_lib.BaseTestCase):
    """Tests the TSK attribute."""

    # pylint: disable=protected-access

    _INODE_A_FILE = 19

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["hfsplus.raw"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec
        )
        self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK, location="/", parent=self._raw_path_spec
        )

        self._file_system = tsk_file_system.TSKFileSystem(
            self._resolver_context, self._tsk_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testInitialize(self):
        """Tests the __init__ function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK,
            inode=self._INODE_A_FILE,
            location="/a_directory/a_file",
            parent=self._raw_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        pytsk_attribute = next(file_entry._tsk_file)
        self.assertIsNotNone(pytsk_attribute)

        test_attribute = tsk_attribute.TSKAttribute(
            file_entry._tsk_file, pytsk_attribute
        )
        self.assertIsNotNone(test_attribute)

        with self.assertRaises(errors.BackEndError):
            tsk_attribute.TSKAttribute(None, pytsk_attribute)

        with self.assertRaises(errors.BackEndError):
            tsk_attribute.TSKAttribute(file_entry._tsk_file, None)


class TSKExtendedAttributeTest(shared_test_lib.BaseTestCase):
    """Tests the TSK extended attribute."""

    # pylint: disable=protected-access

    _INODE_A_FILE = 19

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["hfsplus.raw"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec
        )
        self._tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK, location="/", parent=self._raw_path_spec
        )

        self._file_system = tsk_file_system.TSKFileSystem(
            self._resolver_context, self._tsk_path_spec
        )
        self._file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testInitialize(self):
        """Tests the __init__ function."""
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK,
            inode=self._INODE_A_FILE,
            location="/a_directory/a_file",
            parent=self._raw_path_spec,
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(file_entry)

        pytsk_attribute = next(file_entry._tsk_file)
        self.assertIsNotNone(pytsk_attribute)
        self.assertEqual(pytsk_attribute.info.name, b"myxattr")

        test_attribute = tsk_attribute.TSKExtendedAttribute(
            file_entry._tsk_file, pytsk_attribute
        )
        self.assertIsNotNone(test_attribute)


class TSKNTFSAttributeTestCase(shared_test_lib.BaseTestCase):
    """Shared functionality for testing TSK NTFS attributes."""

    # pylint: disable=protected-access

    # MFT entry and location (without leading path segment separator) of
    # the test file entries.
    _TEST_FILE_ENTRIES = [
        (0, ["$MFT"]),
        (5, []),
        (9, ["$Secure"]),
        (64, ["a_directory"]),
        (65, ["a_directory", "a_file"]),
        (66, ["passwords.txt"]),
        (67, ["a_directory", "another_file"]),
    ]

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["ntfs.raw"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec
        )

        tsk_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK, location="/", parent=self._raw_path_spec
        )
        self._tsk_file_system = tsk_file_system.TSKFileSystem(
            self._resolver_context, tsk_path_spec
        )
        self._tsk_file_system.Open()

        ntfs_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_NTFS, location="\\", parent=self._raw_path_spec
        )
        self._ntfs_file_system = ntfs_file_system.NTFSFileSystem(
            self._resolver_context, ntfs_path_spec
        )
        self._ntfs_file_system.Open()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def _GetAttributes(self, mft_entry, path_segments, type_indicator):
        """Retrieves the TSK and NTFS back-end attributes of a file entry.

        Args:
          mft_entry (int): MFT entry of the file entry.
          path_segments (list[str]): path segments of the file entry.
          type_indicator (str): attribute type indicator.

        Returns:
          tuple[list[Attribute], list[Attribute]]: TSK and NTFS back-end
              attributes.
        """
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK,
            inode=mft_entry,
            location="/" + "/".join(path_segments),
            parent=self._raw_path_spec,
        )
        tsk_file_entry = self._tsk_file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(tsk_file_entry)

        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_NTFS,
            location="\\" + "\\".join(path_segments),
            mft_entry=mft_entry,
            parent=self._raw_path_spec,
        )
        ntfs_file_entry = self._ntfs_file_system.GetFileEntryByPathSpec(path_spec)
        self.assertIsNotNone(ntfs_file_entry)

        tsk_attributes = [
            attribute
            for attribute in tsk_file_entry.attributes
            if attribute.type_indicator == type_indicator
        ]
        ntfs_attributes = [
            attribute
            for attribute in ntfs_file_entry.attributes
            if attribute.type_indicator == type_indicator
        ]
        return tsk_attributes, ntfs_attributes

    def _TestAttributesMatchNTFSBackEnd(self, type_indicator, property_names):
        """Tests that the TSK attributes match the NTFS back-end attributes.

        Args:
          type_indicator (str): attribute type indicator.
          property_names (list[str]): names of the properties to compare.
        """
        for mft_entry, path_segments in self._TEST_FILE_ENTRIES:
            tsk_attributes, ntfs_attributes = self._GetAttributes(
                mft_entry, path_segments, type_indicator
            )
            self.assertEqual(len(tsk_attributes), len(ntfs_attributes))
            self.assertNotEqual(len(tsk_attributes), 0)

            for tsk_attribute_object, ntfs_attribute_object in zip(
                tsk_attributes, ntfs_attributes
            ):
                for property_name in property_names:
                    tsk_value = getattr(tsk_attribute_object, property_name)
                    ntfs_value = getattr(ntfs_attribute_object, property_name)
                    if property_name.endswith("_time"):
                        tsk_value = tsk_value.timestamp
                        ntfs_value = ntfs_value.timestamp

                    self.assertEqual(
                        tsk_value,
                        ntfs_value,
                        msg=f"MFT entry: {mft_entry:d} property: {property_name:s}",
                    )


class TSKFileNameNTFSAttributeTest(TSKNTFSAttributeTestCase):
    """Tests the TSK NTFS $FILE_NAME attribute."""

    _PROPERTY_NAMES = [
        "access_time",
        "creation_time",
        "entry_modification_time",
        "file_attribute_flags",
        "modification_time",
        "name",
        "name_space",
        "parent_file_reference",
    ]

    def testAttributeValues(self):
        """Tests the attribute values."""
        tsk_attributes, _ = self._GetAttributes(
            65, ["a_directory", "a_file"], definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME
        )
        self.assertEqual(len(tsk_attributes), 1)

        test_attribute = tsk_attributes[0]
        self.assertIsInstance(test_attribute, tsk_attribute.TSKFileNameNTFSAttribute)
        self.assertEqual(
            test_attribute.attribute_type, pytsk3.TSK_FS_ATTR_TYPE_NTFS_FNAME
        )
        self.assertEqual(test_attribute.file_attribute_flags, 0x00000020)
        self.assertEqual(test_attribute.name, "a_file")
        self.assertEqual(test_attribute.name_space, 0)
        self.assertEqual(test_attribute.parent_file_reference, 0x1000000000040)

        date_time_string = test_attribute.creation_time.CopyToDateTimeStringISO8601()
        self.assertEqual(date_time_string, "2019-08-31T10:22:59.9567496+00:00")

    def testAttributesMatchNTFSBackEnd(self):
        """Tests that the attributes match the NTFS back-end."""
        self._TestAttributesMatchNTFSBackEnd(
            definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME, self._PROPERTY_NAMES
        )


class TSKStandardInformationNTFSAttributeTest(TSKNTFSAttributeTestCase):
    """Tests the TSK NTFS $STANDARD_INFORMATION attribute."""

    _PROPERTY_NAMES = [
        "access_time",
        "creation_time",
        "entry_modification_time",
        "file_attribute_flags",
        "modification_time",
        "owner_identifier",
        "security_descriptor_identifier",
        "update_sequence_number",
    ]

    def testAttributeValues(self):
        """Tests the attribute values."""
        tsk_attributes, _ = self._GetAttributes(
            65,
            ["a_directory", "a_file"],
            definitions.ATTRIBUTE_TYPE_NTFS_STANDARD_INFORMATION,
        )
        self.assertEqual(len(tsk_attributes), 1)

        test_attribute = tsk_attributes[0]
        self.assertIsInstance(
            test_attribute, tsk_attribute.TSKStandardInformationNTFSAttribute
        )
        self.assertEqual(test_attribute.attribute_type, pytsk3.TSK_FS_ATTR_TYPE_NTFS_SI)
        self.assertEqual(test_attribute.file_attribute_flags, 0x00000020)

        # The $STANDARD_INFORMATION attribute of this file entry is 48 bytes
        # of size and does not contain an owner identifier.
        self.assertIsNone(test_attribute.owner_identifier)
        self.assertIsNone(test_attribute.security_descriptor_identifier)
        self.assertIsNone(test_attribute.update_sequence_number)

        date_time_string = (
            test_attribute.modification_time.CopyToDateTimeStringISO8601()
        )
        self.assertEqual(date_time_string, "2019-08-31T10:22:59.9581788+00:00")

        # The $STANDARD_INFORMATION attribute of $MFT is 72 bytes of size.
        tsk_attributes, _ = self._GetAttributes(
            0, ["$MFT"], definitions.ATTRIBUTE_TYPE_NTFS_STANDARD_INFORMATION
        )
        self.assertEqual(len(tsk_attributes), 1)

        test_attribute = tsk_attributes[0]
        self.assertEqual(test_attribute.owner_identifier, 0)
        self.assertEqual(test_attribute.security_descriptor_identifier, 0)
        self.assertEqual(test_attribute.update_sequence_number, 0)

    def testAttributesMatchNTFSBackEnd(self):
        """Tests that the attributes match the NTFS back-end."""
        self._TestAttributesMatchNTFSBackEnd(
            definitions.ATTRIBUTE_TYPE_NTFS_STANDARD_INFORMATION, self._PROPERTY_NAMES
        )


if __name__ == "__main__":
    unittest.main()
