#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvhdi."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import errors
from dfvfs.path import os_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.path import vhdi_path_spec

from tests.file_io import test_lib


class Version1DynamicVHDIFileTest(test_lib.Ext2ImageFileTestCase):
  """Tests the VHDI file-like object on a dynamic VHD image file."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(Version1DynamicVHDIFileTest, self).setUp()
    test_file = self._GetTestFilePath(['ext2.vhd'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._vhdi_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._vhdi_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = vhdi_path_spec.VHDIPathSpec(parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._vhdi_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._vhdi_path_spec)


class Version1DifferentialVHDIFileTest(test_lib.ImageFileTestCase):
  """Tests the VHDI file-like object on a differential VHD image file."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(Version1DifferentialVHDIFileTest, self).setUp()
    test_file = self._GetTestFilePath(['image-differential.vhd'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._vhdi_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._vhdi_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = vhdi_path_spec.VHDIPathSpec(parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._vhdi_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._vhdi_path_spec)


class Version2VHDIFileTest(test_lib.Ext2ImageFileTestCase):
  """Tests the VHDI file-like object on a VHDX image file."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(Version2VHDIFileTest, self).setUp()
    test_file = self._GetTestFilePath(['ext2.vhdx'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._vhdi_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._vhdi_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = vhdi_path_spec.VHDIPathSpec(parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._vhdi_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._vhdi_path_spec)


class WindowsVersion1DifferentialVHDIFileTestFAT(
    test_lib.WindowsFATImageFileTestCase):
  """Tests the VHDI file-like object on a differential VHD image file."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion1DifferentialVHDIFileTestFAT, self).setUp()

    test_file = self._GetTestFilePath(['fat-differential.vhd'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


class WindowsVersion1DifferentialVHDIFileTestNTFS(
    test_lib.WindowsNTFSImageFileTestCase):
  """Tests the VHDI file-like object on a differential VHD image file."""

  _MFT_ENTRY_ANOTHER_FILE = 37
  _MFT_ENTRY_PASSWORDS_TXT = 36

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion1DifferentialVHDIFileTestNTFS, self).setUp()

    test_file = self._GetTestFilePath(['ntfs-differential.vhd'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


class WindowsVersion1DynamicVHDIFileTest(test_lib.WindowsNTFSImageFileTestCase):
  """Tests the VHDI file-like object on a dynamic VHD image file."""

  _MFT_ENTRY_ANOTHER_FILE = 36
  _MFT_ENTRY_PASSWORDS_TXT = 35

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion1DynamicVHDIFileTest, self).setUp()

    test_file = self._GetTestFilePath(['ntfs-dynamic.vhd'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


class WindowsVersion1FixedVHDIFileTest(test_lib.WindowsNTFSImageFileTestCase):
  """Tests the VHDI file-like object on a fixed VHD image file."""

  _MFT_ENTRY_ANOTHER_FILE = 36
  _MFT_ENTRY_PASSWORDS_TXT = 35

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion1FixedVHDIFileTest, self).setUp()

    test_file = self._GetTestFilePath(['ntfs-fixed.vhd'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


class WindowsVersion2DifferentialVHDIFileTestFAT(
    test_lib.WindowsFATImageFileTestCase):
  """Tests the VHDI file-like object on a differential VHDX image file."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion2DifferentialVHDIFileTestFAT, self).setUp()

    test_file = self._GetTestFilePath(['fat-differential.vhdx'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


class WindowsVersion2DifferentialVHDIFileTestNTFS(
    test_lib.WindowsNTFSImageFileTestCase):
  """Tests the VHDI file-like object on a differential VHDX image file."""

  _MFT_ENTRY_ANOTHER_FILE = 36
  _MFT_ENTRY_PASSWORDS_TXT = 35

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion2DifferentialVHDIFileTestNTFS, self).setUp()

    test_file = self._GetTestFilePath(['ntfs-differential.vhdx'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


class WindowsVersion2DynamicVHDIFileTest(test_lib.WindowsNTFSImageFileTestCase):
  """Tests the VHDI file-like object on a dynamic VHDX image file."""

  _MFT_ENTRY_ANOTHER_FILE = 36
  _MFT_ENTRY_PASSWORDS_TXT = 35

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion2DynamicVHDIFileTest, self).setUp()

    test_file = self._GetTestFilePath(['ntfs-dynamic.vhdx'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


class WindowsVersion2FixedVHDIFileTest(test_lib.WindowsNTFSImageFileTestCase):
  """Tests the VHDI file-like object on a fixed VHDX image file."""

  _MFT_ENTRY_ANOTHER_FILE = 36
  _MFT_ENTRY_PASSWORDS_TXT = 35

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(WindowsVersion2FixedVHDIFileTest, self).setUp()

    test_file = self._GetTestFilePath(['ntfs-fixed.vhdx'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(
        parent=self._os_path_spec)
    self._partition_path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p1', parent=self._vhdi_path_spec)

  def testOpenCloseMFTEntry(self):
    """Test the open and close functionality using a MFT entry."""
    self._TestOpenCloseMFTEntry(self._partition_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._partition_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._partition_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._partition_path_spec)


if __name__ == '__main__':
  unittest.main()
