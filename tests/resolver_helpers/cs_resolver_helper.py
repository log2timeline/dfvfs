#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the CS resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import cs_resolver_helper

from tests.resolver_helpers import test_lib


class CSResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the CS resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(CSResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['fvdetest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    self._gpt_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_GPT, location='/p1',
        parent=test_qcow_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    test_cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/',
        parent=self._gpt_path_spec)

    resolver_helper_object = cs_resolver_helper.CSResolverHelper()
    self._TestNewFileObject(resolver_helper_object, test_cs_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_cs_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_CS, location='/',
        parent=self._gpt_path_spec)

    resolver_helper_object = cs_resolver_helper.CSResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_cs_path_spec)


if __name__ == '__main__':
  unittest.main()
