#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encrypted stream file-like object."""

import os
import unittest

from dfvfs.file_io import encrypted_stream_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class AESEncryptedStreamWithKeyChainTest(test_lib.PaddedSyslogTestCase):
  """Tests the AES encrypted stream file-like object.

  The credentials are passed via the key chain.
  """
  _AES_KEY = b'This is a key123'
  _AES_MODE = definitions.ENCRYPTION_MODE_CBC
  _AES_IV = b'This is an IV456'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.aes'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encrypted_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCRYPTED_STREAM,
        encryption_method=definitions.ENCRYPTION_METHOD_AES,
        parent=test_os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'key', self._AES_KEY)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'initialization_vector',
        self._AES_IV)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'cipher_mode', self._AES_MODE)
    self.padding_size = 1

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    file_object.seek(-10 - self.padding_size, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class AESEncryptedStreamTest(test_lib.PaddedSyslogTestCase):
  """The unit test for a AES encrypted stream file-like object.

  The credentials are passed via the path specification.
  """

  _AES_CIPHER_MODE = definitions.ENCRYPTION_MODE_CBC
  _AES_INITIALIZATION_VECTOR = b'This is an IV456'
  _AES_KEY = b'This is a key123'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.aes'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encrypted_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCRYPTED_STREAM,
        cipher_mode=self._AES_CIPHER_MODE,
        encryption_method=definitions.ENCRYPTION_METHOD_AES,
        initialization_vector=self._AES_INITIALIZATION_VECTOR,
        key=self._AES_KEY, parent=test_os_path_spec)
    self.padding_size = 1

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    file_object.seek(-10 - self.padding_size, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class BlowfishEncryptedStreamWithKeyChainTest(test_lib.PaddedSyslogTestCase):
  """Tests the Blowfish encrypted stream file-like object.

  The credentials are passed via the key chain.
  """
  _BLOWFISH_KEY = b'This is a key123'
  _BLOWFISH_MODE = definitions.ENCRYPTION_MODE_CBC
  _BLOWFISH_IV = b'This IV!'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.blowfish'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encrypted_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCRYPTED_STREAM,
        encryption_method=definitions.ENCRYPTION_METHOD_BLOWFISH,
        parent=test_os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'key', self._BLOWFISH_KEY)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'initialization_vector',
        self._BLOWFISH_IV)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'cipher_mode', self._BLOWFISH_MODE)
    self.padding_size = 1

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    file_object.seek(-10 - self.padding_size, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class DES3EncryptedStreamWithKeyChainTest(test_lib.PaddedSyslogTestCase):
  """Tests the Triple DES encrypted stream file-like object.

  The credentials are passed via the key chain.
  """
  _DES3_KEY = b'This is a key123'
  _DES3_MODE = definitions.ENCRYPTION_MODE_CBC
  _DES3_IV = b'This IV!'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.des3'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encrypted_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCRYPTED_STREAM,
        encryption_method=definitions.ENCRYPTION_METHOD_DES3,
        parent=test_os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'key', self._DES3_KEY)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'initialization_vector',
        self._DES3_IV)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'cipher_mode', self._DES3_MODE)
    self.padding_size = 1

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestGetSizeFileObject(file_object)

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestSeekFileObject(file_object)

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    file_object.seek(-10 - self.padding_size, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    self._TestReadFileObject(file_object)


class RC4EncryptedStreamWithKeyChainTest(test_lib.SylogTestCase):
  """Tests the RC4 encrypted stream file-like object.

  The credentials are passed via the key chain.
  """
  _RC4_KEY = b'rc4test'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_path = self._GetTestFilePath(['syslog.rc4'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._encrypted_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ENCRYPTED_STREAM,
        encryption_method=definitions.ENCRYPTION_METHOD_RC4,
        parent=test_os_path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, 'key', self._RC4_KEY)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    try:
      self._TestGetSizeFileObject(file_object)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy support')

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    try:
      self._TestGetSizeFileObject(file_object)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy support')

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    try:
      self._TestSeekFileObject(file_object)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy support')

    # TODO: Test SEEK_CUR after open.

    # Test SEEK_END after open.
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context, self._encrypted_stream_path_spec)
    file_object.Open()

    try:
      self._TestReadFileObject(file_object)
    except errors.BackEndError:
      raise unittest.SkipTest('missing cryptograpy support')


if __name__ == '__main__':
  unittest.main()
