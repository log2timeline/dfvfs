#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the compressed stream resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import compressed_stream_resolver_helper

from tests.resolver_helpers import test_lib


class CompressedStreamResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the compressed stream resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CompressedStreamResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['syslog.bz2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._compressed_stream_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_COMPRESSED_STREAM,
        compression_method=definitions.COMPRESSION_METHOD_BZIP2,
        parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = (
        compressed_stream_resolver_helper.CompressedStreamResolverHelper())
    self._TestNewFileObject(
        resolver_helper_object, self._compressed_stream_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = (
        compressed_stream_resolver_helper.CompressedStreamResolverHelper())
    self._TestNewFileSystem(
        resolver_helper_object, self._compressed_stream_path_spec)


if __name__ == '__main__':
  unittest.main()
