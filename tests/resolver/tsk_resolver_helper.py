#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the SleuthKit (TSK) resolver helper implementation."""

import unittest

from dfvfs.resolver import tsk_resolver_helper
from tests.resolver import test_lib


class TSKResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the SleuthKit (TSK) resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = tsk_resolver_helper.TSKResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = tsk_resolver_helper.TSKResolverHelper()
    self._TestNewFileSystem(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
