#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the CPIO resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import cpio_resolver_helper

from tests.resolver_helpers import test_lib


class CPIOResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the CPIO resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CPIOResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['syslog.bin.cpio'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    test_cpio_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CPIO, location='/',
        parent=self._os_path_spec)

    resolver_helper_object = cpio_resolver_helper.CPIOResolverHelper()
    self._TestNewFileObject(resolver_helper_object, test_cpio_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_cpio_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CPIO, location='/',
        parent=self._os_path_spec)

    resolver_helper_object = cpio_resolver_helper.CPIOResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_cpio_path_spec)


if __name__ == '__main__':
  unittest.main()
