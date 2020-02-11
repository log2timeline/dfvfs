#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the LUKSDE resolver helper implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver_helpers import luksde_resolver_helper

from tests.resolver_helpers import test_lib


class LUKSDEResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the LUKSDE resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = luksde_resolver_helper.LUKSDEResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = luksde_resolver_helper.LUKSDEResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
