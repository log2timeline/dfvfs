#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the XFS resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import xfs_resolver_helper

from tests.resolver_helpers import test_lib


class XFSResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the XFS resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = xfs_resolver_helper.XFSResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_path = self._GetTestFilePath(['xfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_xfs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_XFS, location='/',
        parent=test_raw_path_spec)

    resolver_helper_object = xfs_resolver_helper.XFSResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_xfs_path_spec)


if __name__ == '__main__':
  unittest.main()
