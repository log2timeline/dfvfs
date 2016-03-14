#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the path specification resolver."""

import unittest

from dfvfs.resolver import resolver
from tests.resolver import test_lib


class ResolverTest(unittest.TestCase):
  """Class to test the path specification resolver object."""

  def testHelperRegistration(self):
    """Tests the DeregisterHelper and DeregisterHelper functions."""
    # pylint: disable=protected-access
    number_of_resolver_helpers = len(resolver.Resolver._resolver_helpers)

    resolver.Resolver.RegisterHelper(test_lib.TestResolverHelper)
    self.assertEqual(
        len(resolver.Resolver._resolver_helpers),
        number_of_resolver_helpers + 1)

    with self.assertRaises(KeyError):
      resolver.Resolver.RegisterHelper(test_lib.TestResolverHelper)

    resolver.Resolver.DeregisterHelper(test_lib.TestResolverHelper)
    self.assertEqual(
        len(resolver.Resolver._resolver_helpers), number_of_resolver_helpers)


if __name__ == '__main__':
  unittest.main()
