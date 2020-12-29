#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the path specification resolver helper manager."""

import unittest

from dfvfs.resolver_helpers import manager

from tests import test_lib as shared_test_lib
from tests.resolver_helpers import test_lib


class ResolverHelperManagerTest(shared_test_lib.BaseTestCase):
  """Tests the path specification resolver helper manager."""

  # pylint: disable=protected-access

  def testHelperRegistration(self):
    """Tests the DeregisterHelper and DeregisterHelper functions."""
    number_of_resolver_helpers = len(
        manager.ResolverHelperManager._resolver_helpers)

    manager.ResolverHelperManager.RegisterHelper(test_lib.TestResolverHelper)
    self.assertEqual(
        len(manager.ResolverHelperManager._resolver_helpers),
        number_of_resolver_helpers + 1)

    with self.assertRaises(KeyError):
      manager.ResolverHelperManager.RegisterHelper(test_lib.TestResolverHelper)

    manager.ResolverHelperManager.DeregisterHelper(test_lib.TestResolverHelper)
    self.assertEqual(
        len(manager.ResolverHelperManager._resolver_helpers),
        number_of_resolver_helpers)


if __name__ == '__main__':
  unittest.main()
