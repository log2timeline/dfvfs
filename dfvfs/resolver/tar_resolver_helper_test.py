#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the tar resolver helper implementation."""

import unittest

from dfvfs.resolver import tar_resolver_helper
from dfvfs.resolver import test_lib


class TarResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the tar resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = tar_resolver_helper.TarResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = tar_resolver_helper.TarResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
