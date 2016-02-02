#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the TAR extracted file-like object."""

import os
import unittest

from dfvfs.file_io import tar_file_io
from dfvfs.path import os_path_spec
from dfvfs.path import tar_path_spec
from dfvfs.resolver import context
from tests.file_io import test_lib


class TARFileTest(test_lib.SylogTestCase):
  """The unit test for a TAR extracted file-like object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    super(TARFileTest, self).setUp()
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'syslog.tar')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._tar_path_spec = tar_path_spec.TARPathSpec(
        location=u'/syslog', parent=path_spec)

  def testOpenClosePathSpec(self):
    """Test the open and close functionality using a path specification."""
    file_object = tar_file_io.TARFile(self._resolver_context)
    file_object.open(path_spec=self._tar_path_spec)

    self._TestGetSizeFileObject(file_object)

    file_object.close()

  def testSeek(self):
    """Test the seek functionality."""
    file_object = tar_file_io.TARFile(self._resolver_context)
    file_object.open(path_spec=self._tar_path_spec)

    self._TestSeekFileObject(file_object)

    file_object.close()

  def testRead(self):
    """Test the read functionality."""
    file_object = tar_file_io.TARFile(self._resolver_context)
    file_object.open(path_spec=self._tar_path_spec)

    self._TestReadFileObject(file_object)

    file_object.close()


if __name__ == '__main__':
  unittest.main()
