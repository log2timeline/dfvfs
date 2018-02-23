#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the CPIO extracted file-like object."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import cpio_file_io
from dfvfs.path import cpio_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib
from tests.file_io import test_lib


@shared_test_lib.skipUnlessHasTestFile(['syslog.bin.cpio'])
class CPIOBinaryFileTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIOBinaryFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.bin.cpio'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


@shared_test_lib.skipUnlessHasTestFile(['syslog.odc.cpio'])
class CPIOPortableASCIIFileTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIOPortableASCIIFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.odc.cpio'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


@shared_test_lib.skipUnlessHasTestFile(['syslog.newc.cpio'])
class CPIONewASCIIFileTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIONewASCIIFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.newc.cpio'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


@shared_test_lib.skipUnlessHasTestFile(['syslog.crc.cpio'])
class CPIONewASCIIFileWithChecksumTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIONewASCIIFileWithChecksumTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.crc.cpio'])
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(self._resolver_context)
    file_object.open(path_spec=self._cpio_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
