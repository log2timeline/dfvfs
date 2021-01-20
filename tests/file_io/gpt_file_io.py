#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyvsgpt."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory

from tests.file_io import test_lib


class GPTImageFileTest(test_lib.Ext2ImageFileTestCase):
  """Tests the GUID Partition Table (GPT) file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(GPTImageFileTest, self).setUp()
    test_path = self._GetTestFilePath(['gpt.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._gpt_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, entry_index=0,
        parent=test_raw_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._gpt_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._gpt_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._gpt_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._gpt_path_spec)


if __name__ == '__main__':
  unittest.main()
