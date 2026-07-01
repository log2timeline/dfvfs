#!/usr/bin/env python3
"""Tests for the compressed stream file-like object."""

import lzma
import os
import random
import tempfile
import time
import unittest

from dfvfs.file_io import compressed_stream_io
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context

from tests.file_io import test_lib
from tests import test_lib as shared_test_lib


class BZIP2CompressedStreamTest(test_lib.SylogTestCase):
    """The unit test for a BZIP2 compressed stream file-like object."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["syslog.bz2"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._compressed_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_COMPRESSED_STREAM,
            compression_method=definitions.COMPRESSION_METHOD_BZIP2,
            parent=test_os_path_spec,
        )

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenCloseFileObject(self):
        """Test the open and close functionality using a file-like object."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testOpenClosePathSpec(self):
        """Test the open and close functionality using a path specification."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testSeek(self):
        """Test the seek functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestSeekFileObject(file_object)

        # TODO: Test SEEK_CUR after open.

        # Test SEEK_END after open.
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        file_object.seek(-10, os.SEEK_END)
        self.assertEqual(file_object.read(5), b"times")

    def testRead(self):
        """Test the read functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestReadFileObject(file_object)


class LZMACompressedStreamTest(test_lib.SylogTestCase):
    """The unit test for a LZMA compressed stream file-like object."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["syslog.lzma"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._compressed_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_COMPRESSED_STREAM,
            compression_method=definitions.COMPRESSION_METHOD_LZMA,
            parent=test_os_path_spec,
        )

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenCloseFileObject(self):
        """Test the open and close functionality using a file-like object."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testOpenClosePathSpec(self):
        """Test the open and close functionality using a path specification."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testSeek(self):
        """Test the seek functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestSeekFileObject(file_object)

        # TODO: Test SEEK_CUR after open.

        # Test SEEK_END after open.
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        file_object.seek(-10, os.SEEK_END)
        self.assertEqual(file_object.read(5), b"times")

    def testRead(self):
        """Test the read functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestReadFileObject(file_object)


class XZCompressedStreamTest(test_lib.SylogTestCase):
    """The unit test for a XZ compressed stream file-like object."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["syslog.xz"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._compressed_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_COMPRESSED_STREAM,
            compression_method=definitions.COMPRESSION_METHOD_XZ,
            parent=test_os_path_spec,
        )

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenCloseFileObject(self):
        """Test the open and close functionality using a file-like object."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testOpenClosePathSpec(self):
        """Test the open and close functionality using a path specification."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testSeek(self):
        """Test the seek functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestSeekFileObject(file_object)

        # TODO: Test SEEK_CUR after open.

        # Test SEEK_END after open.
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        file_object.seek(-10, os.SEEK_END)
        self.assertEqual(file_object.read(5), b"times")

    def testRead(self):
        """Test the read functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestReadFileObject(file_object)


class ZlibCompressedStreamTest(test_lib.SylogTestCase):
    """The unit test for a zlib compressed stream file-like object."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()
        test_path = self._GetTestFilePath(["syslog.zlib"])
        self._SkipIfPathNotExists(test_path)

        test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=test_path
        )
        self._compressed_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_COMPRESSED_STREAM,
            compression_method=definitions.COMPRESSION_METHOD_ZLIB,
            parent=test_os_path_spec,
        )

    def tearDown(self):
        """Cleans up the needed objects used throughout the test."""
        self._resolver_context.Empty()

    def testOpenCloseFileObject(self):
        """Test the open and close functionality using a file-like object."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testOpenClosePathSpec(self):
        """Test the open and close functionality using a path specification."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestGetSizeFileObject(file_object)

    def testSeek(self):
        """Test the seek functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestSeekFileObject(file_object)

        # TODO: Test SEEK_CUR after open.

        # Test SEEK_END after open.
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        file_object.seek(-10, os.SEEK_END)
        self.assertEqual(file_object.read(5), b"times")

    def testRead(self):
        """Test the read functionality."""
        file_object = compressed_stream_io.CompressedStream(
            self._resolver_context, self._compressed_stream_path_spec
        )
        file_object.Open()

        self._TestReadFileObject(file_object)


class CompressedStreamForwardSeekTest(shared_test_lib.BaseTestCase):
    """Regression test for forward seeks rewinding the decompressor."""

    _STREAM_SIZE = 16 * 1024 * 1024  # 16 MiB
    _NUM_SEEKS = 5000  # forward seeks issued
    _MAX_ELAPSED = 5.0  # seconds before declaring failure

    def setUp(self):
        self._resolver_context = context.Context()

    def tearDown(self):
        self._resolver_context.Empty()

    def testForwardSeekDoesNotRewind(self):
        """Forward seeks must take near constant time regardless of stream size.

        Issues many small read+forward-seek pairs and bails out if the
        loop wall time crosses a generous threshold — failing any
        implementation that restarts decompression on each realignment
        and therefore scales as O(N * stream_size) instead of
        O(N + stream_size).

        Pseudo-random data keeps decompression speed bounded by
        liblzma's per-byte literal cost rather than the near-memcpy
        speed of repeating patterns or an empty file. Without this,
        quadratic/polynomial behavior can hide on fast hardware.
        """

        rng = random.Random(0)
        data = rng.randbytes(self._STREAM_SIZE)
        compressed = lzma.compress(data, format=lzma.FORMAT_XZ, preset=0)

        with tempfile.NamedTemporaryFile(suffix=".xz", delete=False) as temp:
            temp.write(compressed)
            temp.close()
            self.addCleanup(os.unlink, temp.name)

            os_path_spec = path_spec_factory.Factory.NewPathSpec(
                definitions.TYPE_INDICATOR_OS, location=temp.name
            )
            path_spec = path_spec_factory.Factory.NewPathSpec(
                definitions.TYPE_INDICATOR_COMPRESSED_STREAM,
                compression_method=definitions.COMPRESSION_METHOD_XZ,
                parent=os_path_spec,
            )

            file_object = compressed_stream_io.CompressedStream(
                self._resolver_context, path_spec
            )
            file_object.Open()
        try:
            step = (self._STREAM_SIZE - 32) // self._NUM_SEEKS
            start = time.monotonic()
            for i in range(self._NUM_SEEKS):
                offset = i * step
                file_object.seek(offset, os.SEEK_SET)

                self.assertEqual(file_object.read(16), data[offset : offset + 16])
                elapsed = time.monotonic() - start
                if elapsed > self._MAX_ELAPSED:
                    self.fail(
                        f"After {i + 1} forward seeks of a "
                        f"{self._STREAM_SIZE >> 20} MiB stream the loop "
                        f"has run for {elapsed:.2f}s "
                        f"(>{self._MAX_ELAPSED:.0f}s); forward seeks are "
                        f"scaling with stream size rather than completing "
                        f"in constant time."
                    )
        finally:
            file_object.close()


if __name__ == "__main__":
    unittest.main()
