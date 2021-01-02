#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the EXT resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import ext_resolver_helper

from tests.resolver_helpers import test_lib


class EXTResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the EXT resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = ext_resolver_helper.EXTResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_path = self._GetTestFilePath(['ext2.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_ext_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EXT, location='/',
        parent=test_raw_path_spec)

    resolver_helper_object = ext_resolver_helper.EXTResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_ext_path_spec)


if __name__ == '__main__':
  unittest.main()
