#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the FVDE resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import fvde_resolver_helper

from tests.resolver_helpers import test_lib


class FVDEResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the FVDE resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(FVDEResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
        parent=test_qcow_path_spec)
    self._fvde_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_FVDE, parent=test_tsk_partition_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = fvde_resolver_helper.FVDEResolverHelper()
    self._TestNewFileObject(resolver_helper_object, self._fvde_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = fvde_resolver_helper.FVDEResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, self._fvde_path_spec)


if __name__ == '__main__':
  unittest.main()
