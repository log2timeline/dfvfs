#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyqcow."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from tests.file_io import test_lib


class QCOWFileTest(test_lib.ImageFileTestCase):
  """The unit test for the QCOW image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(QCOWFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._qcow_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._qcow_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._qcow_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._qcow_path_spec)


if __name__ == '__main__':
  unittest.main()
