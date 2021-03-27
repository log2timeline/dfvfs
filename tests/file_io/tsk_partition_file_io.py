#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using TSK partition."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory

from tests.file_io import test_lib


class TSKPartitionFileTest(test_lib.MBRPartitionedImageFileTestCase):
  """Tests the SleuthKit (TSK) partition file-like object on MBR partitions."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKPartitionFileTest, self).setUp()
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

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
