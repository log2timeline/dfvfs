#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyluksde."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import errors
from dfvfs.path import luksde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class LUKSDEFileWithKeyChainTest(test_lib.Ext2ImageFileTestCase):
  """Tests the LUKS Drive Encryption file-like object.

  The credentials are passed via the key chain.
  """
  _LUKSDE_PASSWORD = 'luksde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(LUKSDEFileWithKeyChainTest, self).setUp()
    test_file = self._GetTestFilePath(['luks1.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._luksde_path_spec = luksde_path_spec.LUKSDEPathSpec(
        parent=self._os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._luksde_path_spec, 'password', self._LUKSDE_PASSWORD)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._luksde_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._luksde_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = luksde_path_spec.LUKSDEPathSpec(parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._luksde_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._luksde_path_spec)


class LUKSDEFileWithPathSpecCredentialsTest(test_lib.Ext2ImageFileTestCase):
  """Tests the LUKS Drive Encryption file-like object.

  The credentials are passed via the path specification.
  """
  _LUKSDE_PASSWORD = 'luksde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(LUKSDEFileWithPathSpecCredentialsTest, self).setUp()
    test_file = self._GetTestFilePath(['luks1.raw'])
    self._SkipIfPathNotExists(test_file)

    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._luksde_path_spec = luksde_path_spec.LUKSDEPathSpec(
        password=self._LUKSDE_PASSWORD, parent=self._os_path_spec)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._luksde_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._luksde_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = luksde_path_spec.LUKSDEPathSpec(
        password=self._LUKSDE_PASSWORD, parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._luksde_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._luksde_path_spec)


if __name__ == '__main__':
  unittest.main()
