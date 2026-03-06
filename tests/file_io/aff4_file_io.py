#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the file-like object implementation using pyaff4."""

import os
import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests import test_lib as shared_test_lib


class AFF4FileTest(shared_test_lib.BaseTestCase):
  """Tests the AFF4 image file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

    test_path = self._GetTestFilePath(['aff4', 'Base-Linear.aff4'])
    self._SkipIfPathNotExists(test_path)

    self._os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._aff4_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_AFF4, parent=self._os_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def testOpen(self):
    """Tests opening the file-like object."""
    file_object = resolver.Resolver.OpenFileObject(
        self._aff4_path_spec, resolver_context=self._resolver_context)

    self.assertEqual(file_object.get_size(), 268435456)

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_AFF4, parent=self._os_path_spec)
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)

  def testSeek(self):
    """Tests seeking in the file-like object."""
    file_object = resolver.Resolver.OpenFileObject(
        self._aff4_path_spec, resolver_context=self._resolver_context)

    file_object.seek(0x163, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), 0x163)

    file_object.seek(17, os.SEEK_CUR)
    self.assertEqual(file_object.get_offset(), 0x174)

    file_object.seek(-32, os.SEEK_END)
    self.assertEqual(file_object.get_offset(), 268435424)

    with self.assertRaises(IOError):
      file_object.seek(-1, os.SEEK_SET)

    with self.assertRaises(IOError):
      file_object.seek(0, 99)

  def testRead(self):
    """Tests reading from the file-like object."""
    file_object = resolver.Resolver.OpenFileObject(
        self._aff4_path_spec, resolver_context=self._resolver_context)

    file_object.seek(0x163, os.SEEK_SET)
    self.assertEqual(file_object.read(17), b'Invalid partition')

    file_object.seek(16, os.SEEK_END)
    self.assertEqual(file_object.read(), b'')


if __name__ == '__main__':
  unittest.main()
