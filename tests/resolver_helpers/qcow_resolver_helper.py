#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the QCOW image resolver helper implementation."""

import unittest

from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver_helpers import qcow_resolver_helper

from tests.resolver_helpers import test_lib


class QCOWResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the QCOW image resolver helper implementation."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(QCOWResolverHelperTest, self).setUp()

    test_path = self._GetTestFilePath(['ext2.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = qcow_resolver_helper.QCOWResolverHelper()
    self._TestNewFileObject(resolver_helper_object, self._qcow_path_spec)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = qcow_resolver_helper.QCOWResolverHelper()
    self._TestNewFileSystemRaisesNotSupported(
        resolver_helper_object, self._qcow_path_spec)


if __name__ == '__main__':
  unittest.main()
