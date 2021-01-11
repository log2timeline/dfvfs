#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the zip resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import zip_resolver_helper

from tests.resolver_helpers import test_lib


class ZipResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the zip resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(ZipResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['syslog.zip'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    test_zip_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/',
        parent=self._os_path_spec)

    resolver_helper_object = zip_resolver_helper.ZipResolverHelper()
    self._TestNewFileObject(resolver_helper_object, test_zip_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_zip_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_ZIP, location='/',
        parent=self._os_path_spec)

    resolver_helper_object = zip_resolver_helper.ZipResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_zip_path_spec)


if __name__ == '__main__':
  unittest.main()
