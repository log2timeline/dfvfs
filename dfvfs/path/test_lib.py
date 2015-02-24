# -*- coding: utf-8 -*-
"""Shared test cases."""

import unittest

from dfvfs.path import path_spec


class TestPathSpec(path_spec.PathSpec):
  """Test path specification."""

  _IS_SYSTEM_LEVEL = True
  TYPE_INDICATOR = u'TEST'

  def __init__(self, **kwargs):
    """Initializes the path specification object."""
    super(TestPathSpec, self).__init__(parent=None, **kwargs)

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    return self._GetComparable()


class PathSpecTestCase(unittest.TestCase):
  """The unit test case for path specification implementions."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._path_spec = TestPathSpec()
