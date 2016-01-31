#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pysmraw."""

import os
import unittest

from dfvfs.lib import errors
from dfvfs.path import raw_path_spec
from dfvfs.path import os_path_spec
from tests.file_io import test_lib


class RawFileTest(test_lib.ImageFileTestCase):
  """The unit test for the RAW storage media image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(RawFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'ímynd.dd')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=self._os_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._raw_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._raw_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = raw_path_spec.RawPathSpec(parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._raw_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._raw_path_spec)


class SplitRawFileTest(test_lib.ImageFileTestCase):
  """The unit test for the split  storage media image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(SplitRawFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.raw.000')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._raw_path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._raw_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._raw_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._raw_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._raw_path_spec)


if __name__ == '__main__':
  unittest.main()
