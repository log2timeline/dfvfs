#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the EWF image resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import ewf_resolver_helper

from tests.resolver_helpers import test_lib


class EWFResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the EWF image resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = ewf_resolver_helper.EWFResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    test_path = self._GetTestFilePath(['ext2.E01'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_ewf_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_EWF, parent=test_os_path_spec)

    resolver_helper_object = ewf_resolver_helper.EWFResolverHelper()
    self._TestNewFileSystemRaisesNotSupported(
        resolver_helper_object, test_ewf_path_spec)


if __name__ == '__main__':
  unittest.main()
