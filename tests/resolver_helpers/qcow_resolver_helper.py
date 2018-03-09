#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the QCOW image resolver helper implementation."""

from __future__ import unicode_literals

import unittest

from dfvfs.resolver_helpers import qcow_resolver_helper

from tests.resolver_helpers import test_lib


class QCOWResolverHelperTest(test_lib.ResolverHelperTestCase):
  """Tests for the QCOW image resolver helper implementation."""

  def testNewFileObject(self):
    """Tests the NewFileObject function."""
    resolver_helper_object = qcow_resolver_helper.QCOWResolverHelper()
    self._TestNewFileObject(resolver_helper_object)

  def testNewFileSystem(self):
    """Tests the NewFileSystem function."""
    resolver_helper_object = qcow_resolver_helper.QCOWResolverHelper()
    self._TestNewFileSystemRaisesRuntimeError(resolver_helper_object)


if __name__ == '__main__':
  unittest.main()
