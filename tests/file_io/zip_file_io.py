#!/usr/bin/env python3
"""Tests for the zip extracted file-like object."""

import os
import struct
import tempfile
import unittest
import zipfile

from dfvfs.file_io import zip_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class ZipFileTest(test_lib.SyslogTestCase):
    """Tests a zip extracted file-like object."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        super().setUp()
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["zip", "syslog.zip"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._zip_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_ZIP, location="/syslog", parent=test_os_path_spec
        )

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenClosePathSpec(self):
        """Test the open and close functionality using a path specification."""
        file_object = zip_file_io.ZipFile(self._resolver_context, self._zip_path_spec)
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testSeek(self):
        """Test the seek functionality."""
        file_object = zip_file_io.ZipFile(self._resolver_context, self._zip_path_spec)
        file_object.Open()

        self._TestSeekFileObject(file_object)

    def testRead(self):
        """Test the read functionality."""
        file_object = zip_file_io.ZipFile(self._resolver_context, self._zip_path_spec)
        file_object.Open()

        self._TestReadFileObject(file_object)

        # TODO: add tests for read > UNCOMPRESSED_DATA_BUFFER_SIZE


class ZipFileUnsupportedEntryTest(test_lib.SyslogTestCase):
    """Tests a zip extracted file-like object on unsupported entries."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        super().setUp()
        self._resolver_context = context.Context()

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def _GetZipPathSpec(self, path):
        """Retrieves a zip path specification of the syslog entry.

        Args:
          path (str): path of the zip file.

        Returns:
          PathSpec: zip path specification.
        """
        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=path
        )
        return path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_ZIP, location="/syslog", parent=test_os_path_spec
        )

    def _TestOpenRaisesError(self, path_segments):
        """Tests that opening the syslog entry raises an error.

        Args:
          path_segments (list[str]): path segments inside the test data directory.
        """
        test_path = self._GetTestFilePath(path_segments)
        self._SkipIfPathNotExists(test_path)

        zip_path_spec = self._GetZipPathSpec(test_path)

        file_object = zip_file_io.ZipFile(self._resolver_context, zip_path_spec)
        with self.assertRaises(OSError):
            file_object.Open()

        with self.assertRaises(errors.BackEndError):
            resolver.Resolver.OpenFileObject(
                zip_path_spec, resolver_context=self._resolver_context
            )

    def _TestReadCorruptedData(self, relative_offset):
        """Tests that reading corrupted compressed data raises an error.

        Args:
          relative_offset (int): offset of the byte to overwrite relative to the
              start of the compressed data of the syslog entry.
        """
        test_path = self._GetTestFilePath(["zip", "syslog.zip"])
        self._SkipIfPathNotExists(test_path)

        with open(test_path, "rb") as file_object:
            zip_data = bytearray(file_object.read())

        with zipfile.ZipFile(test_path, "r") as zip_file:
            zip_info = zip_file.getinfo("syslog")

        header_offset = zip_info.header_offset
        name_size, extra_field_size = struct.unpack(
            "<HH", zip_data[header_offset + 26 : header_offset + 30]
        )
        data_offset = header_offset + 30 + name_size + extra_field_size

        zip_data[data_offset + relative_offset] = 0

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_directory:
            temp_path = os.path.join(temp_directory, "syslog_corrupted.zip")
            with open(temp_path, "wb") as file_object:
                file_object.write(zip_data)

            zip_path_spec = self._GetZipPathSpec(temp_path)

            file_object = zip_file_io.ZipFile(self._resolver_context, zip_path_spec)
            file_object.Open()

            try:
                with self.assertRaises(OSError):
                    file_object.read()
            finally:
                file_object.close()
                self._resolver_context.Empty()

    def testOpenDeflate64(self):
        """Test the open functionality on a Deflate64 compressed entry.

        The test file was created in test_data with 7-Zip 26.00 using:

        7z a -tzip -mm=Deflate64 zip/syslog_deflate64.zip syslog
        """
        self._TestOpenRaisesError(["zip", "syslog_deflate64.zip"])

    def testOpenZipCrypto(self):
        """Test the open functionality on a ZipCrypto encrypted entry.

        The test file was created in test_data with Info-ZIP Zip 3.0 using:

        zip -P dfvfs zip/syslog_zipcrypto.zip syslog
        """
        self._TestOpenRaisesError(["zip", "syslog_zipcrypto.zip"])

    def testReadCorruptedDeflateData(self):
        """Test the read functionality on corrupted deflate compressed data."""
        # Overwriting the first byte of the deflate stream with 0 results in
        # an invalid stored block length, which zlib reports as an error.
        self._TestReadCorruptedData(0)

    def testReadCorruptedCRC(self):
        """Test the read functionality on data with a CRC-32 mismatch."""
        # Overwriting a byte in the middle of the deflate stream results in
        # data that decompresses but does not match the CRC-32.
        self._TestReadCorruptedData(256)


if __name__ == "__main__":
    unittest.main()
