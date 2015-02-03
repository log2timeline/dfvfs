#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the BDE resolver helper implementation."""

import os
import unittest

from dfvfs.path import bde_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import test_lib as path_spec_test_lib
from dfvfs.resolver import bde_resolver_helper
from dfvfs.resolver import resolver
from dfvfs.resolver import test_lib


class BdeResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the BDE resolver helper implementation."""

  _BDE_PASSWORD = u'bde-TEST'

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(BdeResolverHelperTest, self).setUp()
    test_file = os.path.join(u'test_data', u'bdetogo.raw')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._bde_path_spec = bde_path_spec.BdePathSpec(parent=path_spec)
    resolver.Resolver.key_chain.SetCredential(
        self._bde_path_spec, u'password', self._BDE_PASSWORD)

  def testOpenFileObject(self):
    """Tests the OpenFileObject function."""
    resolver_helper_object = bde_resolver_helper.BdeResolverHelper()
    self._TestOpenFileObject(resolver_helper_object, self._bde_path_spec)

  def testOpenFileSystem(self):
    """Tests the OpenFileSystem function."""
    resolver_helper_object = bde_resolver_helper.BdeResolverHelper()
    self._TestOpenFileSystem(resolver_helper_object, self._bde_path_spec)

    path_spec = path_spec_test_lib.TestPathSpec()
    self._TestOpenFileSystemRaises(resolver_helper_object, path_spec)


if __name__ == '__main__':
  unittest.main()
