#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyewf."""

import os
import unittest

from dfvfs.file_io import test_lib
from dfvfs.path import ewf_path_spec
from dfvfs.path import os_path_spec


class EwfFileTest(test_lib.ImageFileTestCase):
  """The unit test for the EWF image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(EwfFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.E01')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._ewf_path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._ewf_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._ewf_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._ewf_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._ewf_path_spec)


class SplitEwfFileTest(test_lib.PartitionedImageFileTestCase):
  """The unit test for the split EWF image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(SplitEwfFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image-split.E01')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._ewf_path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

  def testOpenClose(self):
    """Test the open and close functionality."""
    self._TestOpenClose(self._ewf_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._ewf_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._ewf_path_spec)


if __name__ == '__main__':
  unittest.main()
