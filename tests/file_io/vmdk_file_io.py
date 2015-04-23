#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvmdk."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import vmdk_path_spec
from tests.file_io import test_lib


class VmdkFileTest(test_lib.ImageFileTestCase):
  """The unit test for the VMDK image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(VmdkFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.vmdk')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vmdk_path_spec = vmdk_path_spec.VmdkPathSpec(parent=path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._vmdk_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._vmdk_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._vmdk_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._vmdk_path_spec)


if __name__ == '__main__':
  unittest.main()
