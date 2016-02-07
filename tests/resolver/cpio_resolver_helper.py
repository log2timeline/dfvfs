#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the CPIO resolver helper implementation."""

import unittest

from dfvfs.resolver import cpio_resolver_helper
from tests.resolver import test_lib


class CPIOResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the CPIO resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = cpio_resolver_helper.CPIOResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = cpio_resolver_helper.CPIOResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
