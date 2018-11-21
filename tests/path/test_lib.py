# -*- coding: utf-8 -*-
"""Shared test cases."""

from __future__ import unicode_literals

from dfvfs.path import path_spec

from tests import test_lib as shared_test_lib


class TestPathSpec(path_spec.PathSpec):
  """Test path specification."""

  _IS_SYSTEM_LEVEL = True
  TYPE_INDICATOR = 'TEST'

  def __init__(self, **kwargs):
    """Initializes a test path specification."""
    super(TestPathSpec, self).__init__(parent=None, **kwargs)

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable()


class PathSpecTestCase(shared_test_lib.BaseTestCase):
  """The unit test case for path specification implementations."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._path_spec = TestPathSpec()
