#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the zip resolver helper implementation."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import test_lib as path_spec_test_lib
from dfvfs.path import zip_path_spec
from dfvfs.resolver import test_lib
from dfvfs.resolver import zip_resolver_helper


class ZipResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the zip resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(ZipResolverHelperTest, self).setUp()
    test_file = os.path.join(u'test_data', u'syslog.zip')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._zip_path_spec = zip_path_spec.ZipPathSpec(
        location=u'/syslog', parent=path_spec)

  def testOpenFileObject(self):
    """Tests the OpenFileObject function."""
    resolver_helper_object = zip_resolver_helper.ZipResolverHelper()
    self._TestOpenFileObject(resolver_helper_object, self._zip_path_spec)

  def testOpenFileSystem(self):
    """Tests the OpenFileSystem function."""
    resolver_helper_object = zip_resolver_helper.ZipResolverHelper()
    self._TestOpenFileSystem(resolver_helper_object, self._zip_path_spec)

    path_spec = path_spec_test_lib.TestPathSpec()
    self._TestOpenFileSystemRaises(resolver_helper_object, path_spec)


if __name__ == '__main__':
  unittest.main()
