#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the tar resolver helper implementation."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import tar_path_spec
from dfvfs.path import test_lib as path_spec_test_lib
from dfvfs.resolver import tar_resolver_helper
from dfvfs.resolver import test_lib


class TarResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the tar resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TarResolverHelperTest, self).setUp()
    test_file = os.path.join(u'test_data', u'syslog.tar')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tar_path_spec = tar_path_spec.TarPathSpec(
        location=u'/syslog', parent=path_spec)

  def testOpenFileObject(self):
    """Tests the OpenFileObject function."""
    resolver_helper_object = tar_resolver_helper.TarResolverHelper()
    self._TestOpenFileObject(resolver_helper_object, self._tar_path_spec)

  def testOpenFileSystem(self):
    """Tests the OpenFileSystem function."""
    resolver_helper_object = tar_resolver_helper.TarResolverHelper()
    self._TestOpenFileSystem(resolver_helper_object, self._tar_path_spec)

    path_spec = path_spec_test_lib.TestPathSpec()
    self._TestOpenFileSystemRaises(resolver_helper_object, path_spec)


if __name__ == '__main__':
  unittest.main()
