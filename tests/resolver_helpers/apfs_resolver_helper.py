#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APFS resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import apfs_resolver_helper

from tests.resolver_helpers import test_lib


class APFSResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the APFS resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = apfs_resolver_helper.APFSResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/apfs1',
        parent=test_raw_path_spec)
    test_apfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS, location='/',
        parent=test_apfs_container_path_spec)

    resolver_helper_object = apfs_resolver_helper.APFSResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_apfs_path_spec)


if __name__ == '__main__':
  unittest.main()
