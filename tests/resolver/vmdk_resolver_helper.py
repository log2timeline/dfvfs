#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the VMDK image resolver helper implementation."""

import unittest

from tests.resolver import test_lib
from dfvfs.resolver import vmdk_resolver_helper


class VmdkResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the VMDK image resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = vmdk_resolver_helper.VmdkResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = vmdk_resolver_helper.VmdkResolverHelper()
    self._TestNewFileSystemRaisesRuntimeError(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
