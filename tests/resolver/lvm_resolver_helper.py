#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the LVM resolver helper implementation."""

import unittest

from dfvfs.resolver import lvm_resolver_helper
from tests.resolver import test_lib


class LVMResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the LVM resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = lvm_resolver_helper.LVMResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = lvm_resolver_helper.LVMResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
