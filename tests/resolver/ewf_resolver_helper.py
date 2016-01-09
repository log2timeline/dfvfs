#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the EWF image resolver helper implementation."""

import unittest

from dfvfs.resolver import ewf_resolver_helper
from tests.resolver import test_lib


class EWFResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the EWF image resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = ewf_resolver_helper.EWFResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = ewf_resolver_helper.EWFResolverHelper()
    self._TestNewFileSystemRaisesRuntimeError(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
