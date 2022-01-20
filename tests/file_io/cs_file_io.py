#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyfvde."""

import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class CSFileTestWithKeyChainTest(test_lib.ImageFileTestCase):
  """Tests the Core Storage (CS) file-like object.

  The credentials are passed via the key chain.
  """

  _FVDE_PASSWORD = 'fvde-TEST'

  _INODE_PASSWORDS_TXT = 26
  _INODE_ANOTHER_FILE = 24

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CSFileTestWithKeyChainTest, self).setUp()
    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    self._tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_qcow_path_spec)
    self._cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._tsk_partition_path_spec,
        volume_index=0)

    resolver.Resolver.key_chain.SetCredential(
        self._cs_path_spec, 'password', self._FVDE_PASSWORD)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._cs_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._cs_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/cs1',
        parent=self._tsk_partition_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._cs_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._cs_path_spec)


class CSFileWithPathSpecCredentialsTest(test_lib.ImageFileTestCase):
  """Tests the Core Storage (CS) file-like object.

  The credentials are passed via the path specification.
  """
  _FVDE_PASSWORD = 'fvde-TEST'

  _INODE_PASSWORDS_TXT = 26
  _INODE_ANOTHER_FILE = 24

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CSFileWithPathSpecCredentialsTest, self).setUp()
    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    self._tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_qcow_path_spec)
    self._cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._tsk_partition_path_spec,
        password=self._FVDE_PASSWORD, volume_index=0)

  def testOpenCloseInode(self):
    """Test the open and close functionality using an inode."""
    self._TestOpenCloseInode(self._cs_path_spec)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    self._TestOpenCloseLocation(self._cs_path_spec)

    # Try open with a path specification that has no parent.
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/cs1',
        parent=self._tsk_partition_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(path_spec)

  def testSeek(self):
    """Test the seek functionality."""
    self._TestSeek(self._cs_path_spec)

  def testRead(self):
    """Test the read functionality."""
    self._TestRead(self._cs_path_spec)


if __name__ == '__main__':
  unittest.main()
