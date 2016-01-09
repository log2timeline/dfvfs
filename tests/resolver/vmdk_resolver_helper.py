#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the VMDK image resolver helper implementation."""

import unittest

from dfvfs.resolver import vmdk_resolver_helper
from tests.resolver import test_lib


class VMDKResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the VMDK image resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = vmdk_resolver_helper.VMDKResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = vmdk_resolver_helper.VMDKResolverHelper()
    self._TestNewFileSystemRaisesRuntimeError(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
