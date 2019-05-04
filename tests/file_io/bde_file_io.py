#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pybde."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import errors
from dfvfs.path import bde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class BDEFileWithKeyChainTest(test_lib.ImageFileTestCase):
  """Tests the BitLocker Drive Encryption (BDE) file-like object.

  The credentials are passed via the key chain.
  """
  _BDE_PASSWORD = 'bde-TEST'

  _INODE_PASSWORDS_TXT = 8
  _INODE_ANOTHER_FILE = 582

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(BDEFileWithKeyChainTest, self).setUp()
    test_file = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._bde_path_spec = bde_path_spec.BDEPathSpec(parent=self._os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._bde_path_spec, 'password', self._BDE_PASSWORD)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._bde_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._bde_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = bde_path_spec.BDEPathSpec(parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._bde_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._bde_path_spec)


class BDEFileWithPathSpecCredentialsTest(test_lib.ImageFileTestCase):
  """Tests the BitLocker Drive Encryption (BDE) file-like object.

  The credentials are passed via the path specification.
  """
  _BDE_PASSWORD = 'bde-TEST'

  _INODE_PASSWORDS_TXT = 8
  _INODE_ANOTHER_FILE = 582

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(BDEFileWithPathSpecCredentialsTest, self).setUp()
    test_file = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._bde_path_spec = bde_path_spec.BDEPathSpec(
        password=self._BDE_PASSWORD, parent=self._os_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._bde_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._bde_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = bde_path_spec.BDEPathSpec(
        password=self._BDE_PASSWORD, parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._bde_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._bde_path_spec)


if __name__ == '__main__':
  unittest.main()
