#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using TSK partition."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec

from tests.file_io import test_lib


class TSKPartitionFileTest(test_lib.MBRPartitionedImageFileTestCase):
  """Tests the SleuthKit (TSK) partition file-like object on MBR partitions."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKPartitionFileTest, self).setUp()
    test_file = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_file)

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
