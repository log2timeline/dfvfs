#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the PHDI image resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import phdi_resolver_helper

from tests.resolver_helpers import test_lib


class PHDIResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the PHDI image resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(PHDIResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['hfsplus.hdd', 'DiskDescriptor.xml'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._phdi_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_PHDI, parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = phdi_resolver_helper.PHDIResolverHelper()
    self._TestNewFileObject(resolver_helper_object, self._phdi_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = phdi_resolver_helper.PHDIResolverHelper()
    self._TestNewFileSystemRaisesNotSupported(
        resolver_helper_object, self._phdi_path_spec)


if __name__ == '__main__':
  unittest.main()
