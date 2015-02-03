#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the QCOW image resolver helper implementation."""

import os
import unittest

from dfvfs.path import qcow_path_spec
from dfvfs.path import os_path_spec
from dfvfs.resolver import qcow_resolver_helper
from dfvfs.resolver import test_lib


class QcowResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the QCOW image resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(QcowResolverHelperTest, self).setUp()
    test_file = os.path.join(u'test_data', u'image.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)

  def testOpenFileObject(self):
    """Tests the OpenFileObject function."""
    resolver_helper_object = qcow_resolver_helper.QcowResolverHelper()
    self._TestOpenFileObject(resolver_helper_object, self._qcow_path_spec)

  def testOpenFileSystem(self):
    """Tests the OpenFileSystem function."""
    resolver_helper_object = qcow_resolver_helper.QcowResolverHelper()

    with self.assertRaises(RuntimeError):
      _ = resolver_helper_object.OpenFileSystem(
          self._qcow_path_spec, self._resolver_context)


if __name__ == '__main__':
  unittest.main()
