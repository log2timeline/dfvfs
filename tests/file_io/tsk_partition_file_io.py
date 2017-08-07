#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using TSK partition."""

from __future__ import unicode_literals

import unittest

from dfvfs.path import os_path_spec

from tests import test_lib as shared_test_lib
from tests.file_io import test_lib


@shared_test_lib.skipUnlessHasTestFile(['tsk_volume_system.raw'])
class TSKPartitionFileTest(test_lib.PartitionedImageFileTestCase):
  """The unit test for the SleuthKit (TSK) partition file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TSKPartitionFileTest, self).setUp()
    test_file = self._GetTestFilePath(['tsk_volume_system.raw'])
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
