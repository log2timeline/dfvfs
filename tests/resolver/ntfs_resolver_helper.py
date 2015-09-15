#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the NTFS resolver helper implementation."""

import unittest

from dfvfs.resolver import ntfs_resolver_helper
from tests.resolver import test_lib


class NTFSResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the NTFS resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = ntfs_resolver_helper.NTFSResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = ntfs_resolver_helper.NTFSResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
