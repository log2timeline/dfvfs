#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the operating system resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import os_resolver_helper

from tests.resolver_helpers import test_lib


class OSResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the operating system resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    test_path = self._GetTestFilePath(['testdir_os', 'file1.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    resolver_helper_object = os_resolver_helper.OSResolverHelper()
    self._TestNewFileObject(resolver_helper_object, test_os_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    resolver_helper_object = os_resolver_helper.OSResolverHelper()
    self._TestNewFileSystem(resolver_helper_object, test_os_path_spec)


if __name__ == '__main__':
  unittest.main()
