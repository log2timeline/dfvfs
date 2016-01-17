#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvhdi."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import vhdi_path_spec
from tests.file_io import test_lib


class VHDIFileTest(test_lib.ImageFileTestCase):
  """The unit test for the VHD image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(VHDIFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.vhd')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VHDIPathSpec(parent=path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._vhdi_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._vhdi_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._vhdi_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._vhdi_path_spec)


if __name__ == '__main__':
  unittest.main()
