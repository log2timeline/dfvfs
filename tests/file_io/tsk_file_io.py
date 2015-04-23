#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using the SleuthKit (TSK)."""

import os
import unittest

from dfvfs.path import os_path_spec
from tests.file_io import test_lib


class TSKFileTest(test_lib.ImageFileTestCase):
  """The unit test for the SleuthKit (TSK) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'ímynd.dd')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._os_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._os_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._os_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._os_path_spec)


if __name__ == '__main__':
  unittest.main()
