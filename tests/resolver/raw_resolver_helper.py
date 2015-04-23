#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the RAW image resolver helper implementation."""

import unittest

from dfvfs.resolver import raw_resolver_helper
from tests.resolver import test_lib


class RawResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the RAW image resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = raw_resolver_helper.RawResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = raw_resolver_helper.RawResolverHelper()
    self._TestNewFileSystemRaisesRuntimeError(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
