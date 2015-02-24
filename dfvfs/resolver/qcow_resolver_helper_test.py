#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the QCOW image resolver helper implementation."""

import unittest

from dfvfs.resolver import qcow_resolver_helper
from dfvfs.resolver import test_lib


class QcowResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the QCOW image resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = qcow_resolver_helper.QcowResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = qcow_resolver_helper.QcowResolverHelper()
    self._TestNewFileSystemRaisesRuntimeError(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
