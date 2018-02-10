#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the BDE resolver helper implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver_helpers import bde_resolver_helper

from tests.resolver_helpers import test_lib


class BDEResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the BDE resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = bde_resolver_helper.BDEResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = bde_resolver_helper.BDEResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
