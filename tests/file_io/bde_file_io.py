#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pybde."""

import unittest

from dfvfs.file_io import tsk_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class BDEFileWithKeyChainTest(test_lib.FAT12ImageFileTestCase):
  """Tests the BitLocker Drive Encryption (BDE) file-like object.

  The credentials are passed via the key chain.
  """

  _BDE_PASSWORD = 'bde-TEST'

  _IDENTIFIER_ANOTHER_FILE = 582
  _IDENTIFIER_PASSWORDS_TXT = 8

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(BDEFileWithKeyChainTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._bde_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_BDE, parent=self._os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._bde_path_spec, 'password', self._BDE_PASSWORD)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/passwords.txt',
        parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/a_directory/another_file',
        inode=self._IDENTIFIER_ANOTHER_FILE, parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/passwords.txt',
        inode=self._IDENTIFIER_PASSWORDS_TXT, parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestRead(file_object)


class BDEFileWithPathSpecCredentialsTest(test_lib.FAT12ImageFileTestCase):
  """Tests the BitLocker Drive Encryption (BDE) file-like object.

  The credentials are passed via the path specification.
  """

  _BDE_PASSWORD = 'bde-TEST'

  _IDENTIFIER_ANOTHER_FILE = 582
  _IDENTIFIER_PASSWORDS_TXT = 8

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(BDEFileWithPathSpecCredentialsTest, self).setUp()
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['bdetogo.raw'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._bde_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_BDE, parent=self._os_path_spec,
        password=self._BDE_PASSWORD)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseIdentifier(self):
    """Test the open and close functionality using an identifier."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, inode=self._IDENTIFIER_PASSWORDS_TXT,
        parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestOpenCloseIdentifier(file_object)

  def testOpenCloseLocation(self):
    """Test the open and close functionality using a location."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/passwords.txt',
        parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestOpenCloseLocation(file_object)

    # Try open with a path specification that has no parent.
    path_spec.parent = None
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    with self.assertRaises(errors.PathSpecError):
      self._TestOpenCloseLocation(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/a_directory/another_file',
        inode=self._IDENTIFIER_ANOTHER_FILE, parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestSeek(file_object)

  def testRead(self):
    """Test the read functionality."""
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK, location='/passwords.txt',
        inode=self._IDENTIFIER_PASSWORDS_TXT, parent=self._bde_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context, path_spec)

    self._TestRead(file_object)


if __name__ == '__main__':
  unittest.main()
