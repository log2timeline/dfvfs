#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the CPIO extracted file-like object."""

import unittest

from dfvfs.file_io import cpio_file_io
from dfvfs.path import cpio_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests.file_io import test_lib


class CPIOBinaryFileTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIOBinaryFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class CPIOPortableASCIIFileTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIOPortableASCIIFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.odc.cpio'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class CPIONewASCIIFileTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIONewASCIIFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.newc.cpio'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class CPIONewASCIIFileWithChecksumTest(test_lib.SylogTestCase):
  """The unit test for a CPIO extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIONewASCIIFileWithChecksumTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['syslog.crc.cpio'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._cpio_path_spec = cpio_path_spec.CPIOPathSpec(
        location='/syslog', parent=path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

  def testRead(self):
    """Test the read functionality."""
    file_object = cpio_file_io.CPIOFile(
        self._resolver_context, self._cpio_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


if __name__ == '__main__':
  unittest.main()
