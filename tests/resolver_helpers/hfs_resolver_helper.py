#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the HFS resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import hfs_resolver_helper

from tests.resolver_helpers import test_lib


class HFSResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the HFS resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = hfs_resolver_helper.HFSResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_path = self._GetTestFilePath(['hfsplus.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_hfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_HFS, location='/',
        parent=test_raw_path_spec)

    resolver_helper_object = hfs_resolver_helper.HFSResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_hfs_path_spec)


if __name__ == '__main__':
  unittest.main()
