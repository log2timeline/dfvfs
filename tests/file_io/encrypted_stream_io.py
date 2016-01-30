#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the encrypted stream file-like object."""

import os
import unittest

from dfvfs.file_io import encrypted_stream_io
from dfvfs.file_io import os_file_io
from dfvfs.lib import definitions
from dfvfs.path import encrypted_stream_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests.file_io import test_lib


class RC4EncryptedStreamTest(test_lib.SylogTestCase):
  """The unit test for a RC4 encrypted stream file-like object."""

  _RC4_KEY = b'rc4test'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.rc4')
    self._os_path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._encrypted_stream_path_spec = (
        encrypted_stream_path_spec.EncryptedStreamPathSpec(
            encryption_method=definitions.ENCRYPTION_METHOD_RC4,
            parent=self._os_path_spec))
    resolver.Resolver.key_chain.SetCredential(
        self._encrypted_stream_path_spec, u'key', self._RC4_KEY)

  def testOpenCloseFileObject(self):
    """Test the open and close functionality using a file-like object."""
    os_file_object = os_file_io.OSFile(self._resolver_context)
    os_file_object.open(path_spec=self._os_path_spec)
    file_object = encrypted_stream_io.EncryptedStream(
        self._resolver_context,
        encryption_method=definitions.ENCRYPTION_METHOD_RC4,
        file_object=os_file_object)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()
    os_file_object.close()

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = encrypted_stream_io.EncryptedStream(self._resolver_context)
    file_object.open(path_spec=self._encrypted_stream_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
