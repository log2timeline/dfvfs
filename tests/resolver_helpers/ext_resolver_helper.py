#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the EXT resolver helper implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver_helpers import ext_resolver_helper

from tests.resolver_helpers import test_lib


class EXTResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the EXT resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = ext_resolver_helper.EXTResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = ext_resolver_helper.EXTResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
