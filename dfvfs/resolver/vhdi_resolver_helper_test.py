#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the VHD image resolver helper implementation."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import vhdi_path_spec
from dfvfs.resolver import test_lib
from dfvfs.resolver import vhdi_resolver_helper


class VhdiResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the VHD image resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(VhdiResolverHelperTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.vhd')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._vhdi_path_spec = vhdi_path_spec.VhdiPathSpec(parent=path_spec)

  def testOpenFileObject(self):
    """Tests the OpenFileObject function."""
    resolver_helper_object = vhdi_resolver_helper.VhdiResolverHelper()
    self._TestOpenFileObject(resolver_helper_object, self._vhdi_path_spec)

  def testOpenFileSystem(self):
    """Tests the OpenFileSystem function."""
    resolver_helper_object = vhdi_resolver_helper.VhdiResolverHelper()

    with self.assertRaises(RuntimeError):
      _ = resolver_helper_object.OpenFileSystem(
          self._vhdi_path_spec, self._resolver_context)


if __name__ == '__main__':
  unittest.main()
