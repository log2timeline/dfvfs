#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the VMDK image resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import vmdk_resolver_helper

from tests.resolver_helpers import test_lib


class VMDKResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the VMDK image resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(VMDKResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['ext2.vmdk'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._vmdk_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VMDK, parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = vmdk_resolver_helper.VMDKResolverHelper()
    self._TestNewFileObject(resolver_helper_object, self._vmdk_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = vmdk_resolver_helper.VMDKResolverHelper()
    self._TestNewFileSystemRaisesNotSupported(
        resolver_helper_object, self._vmdk_path_spec)


if __name__ == '__main__':
  unittest.main()
