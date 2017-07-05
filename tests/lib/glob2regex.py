#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows Registry searcher."""

from __future__ import unicode_literals

import fnmatch
import unittest

from dfvfs.lib import glob2regex

from tests import test_lib


class Glob2RegexTest(test_lib.BaseTestCase):
  """Tests for the glob to regular expression conversion function."""

  def _Glob2Regex(self, glob_pattern):
    """Converts a glob pattern to a regular expression.

    Args:
      glob_pattern (str): glob pattern.

    Returns:
      _sre.SRE_Pattern: regular expression of the glob pattern.

    Raises:
      ValueError: if the glob pattern cannot be converted.
    """
    # fnmatch.translate() is used to convert a glob into a regular
    # expression. For Python 3.5 and earlier, the resulting regular
    # expression has "\Z(?ms)" defined at its end, which needs to be
    # removed and escapes the forward slash "/", which needs to be
    # undone. Python 3.6 puts the options at the beginning of the
    # regular expression instead.

    fnmatch_regex = fnmatch.translate(glob_pattern)

    for suffix in (r'\Z(?ms)', r')\Z'):
      if fnmatch_regex.endswith(suffix):
        fnmatch_regex = fnmatch_regex[:-len(suffix)]
      if fnmatch_regex.startswith('(?s:'):
        fnmatch_regex = fnmatch_regex[len('(?s:'):]

    fnmatch_regex = fnmatch_regex.replace('\\/', '/')

    return fnmatch_regex

  def testGlob2Regex(self):
    """Tests the Glob2Regex function."""
    regex = glob2regex.Glob2Regex('plain.txt')
    expected_regex = self._Glob2Regex('plain.txt')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('*.txt')
    expected_regex = self._Glob2Regex('*.txt')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('plain?.txt')
    expected_regex = self._Glob2Regex('plain?.txt')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('plain[?].txt')
    expected_regex = self._Glob2Regex('plain[?].txt')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('plai[nN].txt')
    expected_regex = self._Glob2Regex('plai[nN].txt')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('plai[!nN].txt')
    expected_regex = self._Glob2Regex('plai[!nN].txt')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('plai[nN.txt')
    expected_regex = self._Glob2Regex('plai[nN.txt')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('plain.(jpg|txt)')
    expected_regex = self._Glob2Regex('plain.(jpg|txt)')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('.^$*+?{}\\[]|()')
    expected_regex = self._Glob2Regex('.^$*+?{}\\[]|()')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex('[.^$*+?{}\\|()]')
    expected_regex = self._Glob2Regex('[.^$*+?{}\\|()]')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex(u'[\\]]')
    expected_regex = self._Glob2Regex(u'[\\]]')
    self.assertEqual(regex, expected_regex)

    regex = glob2regex.Glob2Regex(u'[]]')
    expected_regex = self._Glob2Regex(u'[]]')
    self.assertEqual(regex, expected_regex)


if __name__ == '__main__':
  unittest.main()
