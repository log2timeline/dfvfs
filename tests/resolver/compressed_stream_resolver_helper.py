#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the compressed stream resolver helper implementation."""

import unittest

from dfvfs.resolver import compressed_stream_resolver_helper
from tests.resolver import test_lib


class CompressedStreamResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the compressed stream resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = (
        compressed_stream_resolver_helper.CompressedStreamResolverHelper())
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = (
        compressed_stream_resolver_helper.CompressedStreamResolverHelper())
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
