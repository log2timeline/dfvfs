#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using TSK partition."""

import os
import unittest

from dfvfs.path import os_path_spec
from tests.file_io import test_lib


class TSKPartitionFileTest(test_lib.PartitionedImageFileTestCase):
  """The unit test for the SleuthKit (TSK) partition file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKPartitionFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'tsk_volume_system.raw')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)

  def testOpenClose(self):
    """Test the open and close functionality."""
    self._TestOpenClose(self._os_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._os_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._os_path_spec)


if __name__ == '__main__':
  unittest.main()
