#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the encrypted stream resolver helper implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver_helpers import encrypted_stream_resolver_helper

from tests.resolver_helpers import test_lib


class EncryptedStreamResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the encrypted stream resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = (
        encrypted_stream_resolver_helper.EncryptedStreamResolverHelper())
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = (
        encrypted_stream_resolver_helper.EncryptedStreamResolverHelper())
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
