#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyfvde."""

import unittest

from dfvfs.file_io import hfs_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class CSFileTest(test_lib.HFSImageFileTestCase):
  """Tests the Core Storage (CS) file-like object."""

  _IDENTIFIER_ANOTHER_FILE = 26
  _IDENTIFIER_PASSWORDS_TXT = 25

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CSFileTest, self).setUp()
    test_path = self._GetTestFilePath(['cs_single_volume.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    self._cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=self._raw_path_spec,
        volume_index=0)

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestRead(file_object)


class CSFileWithKeyChainTest(test_lib.HFSImageFileTestCase):
  """Tests the Core Storage (CS) file-like object.

  The credentials are passed via the key chain.
  """

  _FVDE_PASSWORD = 'fvde-TEST'

  _IDENTIFIER_ANOTHER_FILE = 24
  _IDENTIFIER_PASSWORDS_TXT = 26

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CSFileWithKeyChainTest, self).setUp()
    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_qcow_path_spec)
    self._cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=test_tsk_partition_path_spec,
        volume_index=0)

    resolver.Resolver.key_chain.SetCredential(
        self._cs_path_spec, 'password', self._FVDE_PASSWORD)

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestRead(file_object)


class CSFileWithPathSpecCredentialsTest(test_lib.HFSImageFileTestCase):
  """Tests the Core Storage (CS) file-like object.

  The credentials are passed via the path specification.
  """
  _FVDE_PASSWORD = 'fvde-TEST'

  _IDENTIFIER_ANOTHER_FILE = 24
  _IDENTIFIER_PASSWORDS_TXT = 26

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CSFileWithPathSpecCredentialsTest, self).setUp()
    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_qcow_path_spec)
    self._cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, parent=test_tsk_partition_path_spec,
        password=self._FVDE_PASSWORD, volume_index=0)

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_ANOTHER_FILE,
        location='/a_directory/another_file', parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS,
        identifier=self._IDENTIFIER_PASSWORDS_TXT, location='/passwords.txt',
        parent=self._cs_path_spec)
    file_object = hfs_file_io.HFSFile(self._resolver_context, path_spec)

    self._TestRead(file_object)


if __name__ == '__main__':
  unittest.main()
