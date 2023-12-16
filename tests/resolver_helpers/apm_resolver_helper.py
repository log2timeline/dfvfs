#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the APM resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import apm_resolver_helper

from tests.resolver_helpers import test_lib


class APMResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the APM resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(APMResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['apm.dmg'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._modi_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_MODI, parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    test_apm_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APM, location='/',
        parent=self._modi_path_spec)

    resolver_helper_object = apm_resolver_helper.APMResolverHelper()
    self._TestNewFileObject(resolver_helper_object, test_apm_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_apm_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APM, location='/',
        parent=self._modi_path_spec)

    resolver_helper_object = apm_resolver_helper.APMResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_apm_path_spec)


if __name__ == '__main__':
  unittest.main()
