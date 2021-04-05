#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pymodi."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory

from tests.file_io import test_lib


class SparseImageMODIFileTest(test_lib.HFSImageFileTestCase):
  """Tests the MODI file-like object on a spare image file."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(SparseImageMODIFileTest, self).setUp()
    test_path = self._GetTestFilePath(['hfsplus.sparseimage'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._modi_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_MODI, parent=test_os_path_spec)
    self._tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=self._modi_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._tsk_partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._tsk_partition_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=self._modi_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._tsk_partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._tsk_partition_path_spec)


class ZlibCompressedUDIFMODIFileTest(test_lib.HFSImageFileTestCase):
  """Tests the MODI file-like object on a zlib compressed UDIF image file."""

  _IDENTIFIER_ANOTHER_FILE = 20
  _IDENTIFIER_PASSWORDS_TXT = 22

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(ZlibCompressedUDIFMODIFileTest, self).setUp()
    test_path = self._GetTestFilePath(['hfsplus_zlib.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._modi_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_MODI, parent=test_os_path_spec)
    self._tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=self._modi_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._tsk_partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._tsk_partition_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=self._modi_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._tsk_partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._tsk_partition_path_spec)


if __name__ == '__main__':
  unittest.main()
