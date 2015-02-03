#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the VMDK image resolver helper implementation."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import vmdk_path_spec
from dfvfs.resolver import test_lib
from dfvfs.resolver import vmdk_resolver_helper


class VmdkResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the VMDK image resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(VmdkResolverHelperTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.vmdk')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vmdk_path_spec = vmdk_path_spec.VmdkPathSpec(parent=path_spec)

  def testOpenFileObject(self):
    """Tests the OpenFileObject function."""
    resolver_helper_object = vmdk_resolver_helper.VmdkResolverHelper()
    self._TestOpenFileObject(resolver_helper_object, self._vmdk_path_spec)

  def testOpenFileSystem(self):
    """Tests the OpenFileSystem function."""
    resolver_helper_object = vmdk_resolver_helper.VmdkResolverHelper()

    with self.assertRaises(RuntimeError):
      _ = resolver_helper_object.OpenFileSystem(
          self._vmdk_path_spec, self._resolver_context)


if __name__ == '__main__':
  unittest.main()
