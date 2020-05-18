# -*- coding: utf-8 -*-
"""Shared test case."""

from __future__ import unicode_literals

import os
import unittest


# The path to top of the dfWinReg source tree.
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# The paths below are all derived from the project path directory.
# They are enumerated explicitly here so that they can be overwritten for
# compatibility with different build systems.
TEST_DATA_PATH = os.path.join(PROJECT_PATH, 'test_data')


class BaseTestCase(unittest.TestCase):
  """The base test case."""

  # Show full diff results, part of TestCase so does not follow our naming
  # conventions.
  maxDiff = None

  def _assertSubFileEntries(self, file_entry, expected_sub_file_entry_names):
    """Asserts that sub file entries have match the expected names.

    Args:
      file_entry (FileEntry): file entry.
      expected_sub_file_entry_names (list[str]): expected sub file entry names.
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
    return os.path.join(TEST_DATA_PATH, *path_segments)

  def _SkipIfPathNotExists(self, path):
    """Skips the test if the path does not exist.

    Args:
      path (str): path of a test file.

    Raises:
      SkipTest: if the path does not exist and the test should be skipped.
    """
    if not os.path.exists(path):
      filename = os.path.basename(path)
      raise unittest.SkipTest('missing test file: {0:s}'.format(filename))
