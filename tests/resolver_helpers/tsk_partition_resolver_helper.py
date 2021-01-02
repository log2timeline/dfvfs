#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the TSK partition resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import tsk_partition_resolver_helper

from tests.resolver_helpers import test_lib


class TSKPartitionResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the TSK partition resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = (
        tsk_partition_resolver_helper.TSKPartitionResolverHelper())
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/',
        parent=test_os_path_spec)

    resolver_helper_object = (
        tsk_partition_resolver_helper.TSKPartitionResolverHelper())
    self._TestNewFileSystem(
        resolver_helper_object, test_tsk_partition_path_spec)


if __name__ == '__main__':
  unittest.main()
