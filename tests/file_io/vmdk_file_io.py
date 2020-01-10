#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvmdk."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import errors
from dfvfs.path import os_path_spec
from dfvfs.path import vmdk_path_spec

from tests.file_io import test_lib


class VMDKFileTest(test_lib.Ext2ImageFileTestCase):
  """Tests the VMDK image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(VMDKFileTest, self).setUp()
    test_file = self._GetTestFilePath(['ext2.vmdk'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vmdk_path_spec = vmdk_path_spec.VMDKPathSpec(
        parent=self._os_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._vmdk_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._vmdk_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = vmdk_path_spec.VMDKPathSpec(parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._vmdk_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._vmdk_path_spec)


if __name__ == '__main__':
  unittest.main()
