#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the LUKSDE resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import luksde_resolver_helper

from tests.resolver_helpers import test_lib


class LUKSDEResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the LUKSDE resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(LUKSDEResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['luks1.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._luksde_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LUKSDE, parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = luksde_resolver_helper.LUKSDEResolverHelper()
    self._TestNewFileObject(resolver_helper_object, self._luksde_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = luksde_resolver_helper.LUKSDEResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, self._luksde_path_spec)


if __name__ == '__main__':
  unittest.main()
