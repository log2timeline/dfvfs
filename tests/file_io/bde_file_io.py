#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pybde."""

import os
import unittest

from dfvfs.path import bde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import resolver
from tests.file_io import test_lib


class BDEFileTest(test_lib.ImageFileTestCase):
  """The unit test for the BitLocker Drive Encryption (BDE) file-like object."""

  _BDE_PASSWORD = u'bde-TEST'

  _INODE_PASSWORDS_TXT = 8
  _INODE_ANOTHER_FILE = 582

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(BDEFileTest, self).setUp()
    test_file = os.path.join(u'test_data', u'bdetogo.raw')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._bde_path_spec = bde_path_spec.BDEPathSpec(parent=path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._bde_path_spec, u'password', self._BDE_PASSWORD)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._bde_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._bde_path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._bde_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._bde_path_spec)


if __name__ == '__main__':
  unittest.main()
