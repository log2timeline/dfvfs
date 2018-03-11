# -*- coding: utf-8 -*-
"""Shared test case."""

from __future__ import unicode_literals

import os
import sys
import unittest


def skipUnlessHasTestFile(path_segments):  # pylint: disable=invalid-name
  """Decorator to skip a test if the test file does not exist.

  Args:
    path_segments (list[str]): path segments inside the test data directory.

  Returns:
    function: to invoke.
  """
  fail_unless_has_test_file = getattr(
      unittest, 'fail_unless_has_test_file', False)

  path = os.path.join('test_data', *path_segments)
  if fail_unless_has_test_file or os.path.exists(path):
    return lambda function: function

  if sys.version_info[0] < 3:
    path = path.encode('utf-8')

  # Note that the message should be of type str which is different for
  # different versions of Python.
  return unittest.skip('missing test file: {0:s}'.format(path))


class BaseTestCase(unittest.TestCase):
  """The base test case."""

  _TEST_DATA_PATH = os.path.join(os.getcwd(), 'test_data')

  # Show full diff results, part of TestCase so does not follow our naming
  # conventions.
  maxDiff = None

  def _assertSubFileEntries(self, file_entry, expected_sub_file_entry_names):
    """Helper function that asserts the sub file entries have the
    expected names.

    Args:
      file_entry (FileEntry): file entry.
      sub_file_entry_names (list[str]): sub file entry names.
    """
    self.assertEqual(
        file_entry.number_of_sub_file_entries,
        len(expected_sub_file_entry_names))

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))

  def _GetTestFilePath(self, path_segments):
    """Retrieves the path of a test file in the test data directory.

    Args:
      path_segments (list[str]): path segments inside the test data directory.

    Returns:
      str: path of the test file.
    """
    # Note that we need to pass the individual path segments to os.path.join
    # and not a list.
    return os.path.join(self._TEST_DATA_PATH, *path_segments)
