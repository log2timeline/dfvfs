#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the VSS resolver helper implementation."""

import unittest

from dfvfs.resolver import vshadow_resolver_helper
from tests.resolver import test_lib


class VShadowResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the VSS resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = vshadow_resolver_helper.VShadowResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = vshadow_resolver_helper.VShadowResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
