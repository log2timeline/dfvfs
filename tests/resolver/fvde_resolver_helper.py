#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the FVDE resolver helper implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver import fvde_resolver_helper

from tests.resolver import test_lib


class FVDEResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the FVDE resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = fvde_resolver_helper.FVDEResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = fvde_resolver_helper.FVDEResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
