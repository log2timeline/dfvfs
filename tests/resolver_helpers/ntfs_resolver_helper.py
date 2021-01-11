#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the NTFS resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import ntfs_resolver_helper

from tests.resolver_helpers import test_lib


class NTFSResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the NTFS resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(NTFSResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    test_ntfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._qcow_path_spec)

    resolver_helper_object = ntfs_resolver_helper.NTFSResolverHelper()
    self._TestNewFileObject(resolver_helper_object, test_ntfs_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_ntfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_NTFS, location='\\',
        parent=self._qcow_path_spec)

    resolver_helper_object = ntfs_resolver_helper.NTFSResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_ntfs_path_spec)


if __name__ == '__main__':
  unittest.main()
