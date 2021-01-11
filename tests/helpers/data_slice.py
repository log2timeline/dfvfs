#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the data slice interface for file-like objects."""

import unittest

from dfvfs.helpers import data_slice
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests import test_lib as shared_test_lib


class TextFileTest(shared_test_lib.BaseTestCase):
  """Tests the data slice interface for file-like objects."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testGetItems(self):
    """Test the __getitem__ function."""
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    file_data = data_slice.DataSlice(file_object)

    # Test linear read.
    self.assertEqual(file_data[:20], b'place,user,password\n')
    self.assertEqual(file_data[20:44], b'bank,joesmith,superrich\n')
    self.assertEqual(file_data[44:64], b'alarm system,-,1234\n')
    self.assertEqual(file_data[64:86], b'treasure chest,-,1111\n')
    self.assertEqual(file_data[86:], b'uber secret laire,admin,admin\n')

    # Test non-linear read.
    self.assertEqual(file_data[44:64], b'alarm system,-,1234\n')
    self.assertEqual(file_data[86:], b'uber secret laire,admin,admin\n')
    self.assertEqual(file_data[20:44], b'bank,joesmith,superrich\n')
    self.assertEqual(file_data[:20], b'place,user,password\n')
    self.assertEqual(file_data[64:86], b'treasure chest,-,1111\n')

    # Test edge cases.
    self.assertEqual(file_data[-150:20], b'place,user,password\n')
    self.assertEqual(file_data[86:150], b'uber secret laire,admin,admin\n')

    with self.assertRaises(TypeError):
      file_data['key']  # pylint: disable=pointless-statement

    with self.assertRaises(ValueError):
      file_data[44:64:2]  # pylint: disable=pointless-statement

  def testLen(self):
    """Test the __len__ function."""
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    file_data = data_slice.DataSlice(file_object)

    self.assertEqual(len(file_data), 116)


if __name__ == '__main__':
  unittest.main()
