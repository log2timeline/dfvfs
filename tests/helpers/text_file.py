#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the text file interface for file-like objects."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import os_file_io
from dfvfs.helpers import text_file
from dfvfs.path import os_path_spec
from dfvfs.resolver import context

from tests import test_lib as shared_test_lib


# TODO: Add a test which tests reading a text file which is
# larger than the buffer size, and read lines until it crosses
# that original buffer size (to test if the buffer is correctly
# filled).

class TextFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the text file object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def testReadline(self):
    """Test the readline() function."""
    test_file = self._GetTestFilePath(['another_file'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object)

    line = text_file_object.readline()
    self.assertEqual(line, 'This is another file.\n')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 22)

    text_file_object = text_file.TextFile(file_object)

    line = text_file_object.readline(size=11)
    self.assertEqual(line, 'This is ano')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 11)

    file_object.close()

  def testReadlineWithError(self):
    """Test the readline() function with an encoding error."""
    test_file = self._GetTestFilePath(['another_file_with_error'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object)

    with self.assertRaises(UnicodeDecodeError):
      text_file_object.readline()

    text_file_object = text_file.TextFile(
        file_object, encoding_errors='replace')

    line = text_file_object.readline()
    self.assertEqual(line, 'This is ano\ufffdher file.\n')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 22)

    text_file_object = text_file.TextFile(file_object)

    line = text_file_object.readline(size=11)
    self.assertEqual(line, 'This is ano')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 11)

    file_object.close()

  def testReadlineUTF16(self):
    """Test the readline() function on UTF-16 encoded text."""
    test_file = self._GetTestFilePath(['another_file.utf16'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object, encoding='utf-16-le')

    line = text_file_object.readline()
    self.assertEqual(line, 'This is another file.\n')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 46)

    text_file_object = text_file.TextFile(file_object, encoding='utf-16-le')

    line = text_file_object.readline(size=24)
    self.assertEqual(line, 'This is ano')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 24)

    file_object.close()

  def testReadlineMultipleLines(self):
    """Test the readline() function on multiple lines."""
    test_file = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object)

    line = text_file_object.readline()
    self.assertEqual(line, 'place,user,password\n')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 20)

    line = text_file_object.readline(size=5)
    self.assertEqual(line, 'bank,')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 25)

    line = text_file_object.readline()
    self.assertEqual(line, 'joesmith,superrich\n')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 44)

    line = text_file_object.readline()
    self.assertEqual(line, 'alarm system,-,1234\n')

    offset = text_file_object.get_offset()
    self.assertEqual(offset, 64)

    file_object.close()

  def testReadlineWithEndOfFileTruncation(self):
    """Test the readline() function with specified size at end of file."""
    test_file = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object)

    line = text_file_object.readline(size=24)
    self.assertEqual(line, 'place,user,password\n')
    line = text_file_object.readline(size=24)
    self.assertEqual(line, 'bank,joesmith,superrich\n')
    line = text_file_object.readline(size=24)
    self.assertEqual(line, 'alarm system,-,1234\n')
    line = text_file_object.readline(size=24)
    self.assertEqual(line, 'treasure chest,-,1111\n')
    line = text_file_object.readline(size=30)
    self.assertEqual(line, 'uber secret laire,admin,admin\n')

    file_object.close()

  def testReadlines(self):
    """Test the readlines() function."""
    test_file = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines()

    self.assertEqual(len(lines), 5)
    self.assertEqual(lines[0], 'place,user,password\n')
    self.assertEqual(lines[1], 'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], 'alarm system,-,1234\n')
    self.assertEqual(lines[3], 'treasure chest,-,1111\n')
    self.assertEqual(lines[4], 'uber secret laire,admin,admin\n')

    file_object.close()

  def testReadlinesWithSizeHint(self):
    """Test the readlines() function."""
    test_file = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines(sizehint=60)

    self.assertEqual(len(lines), 3)
    self.assertEqual(lines[0], 'place,user,password\n')
    self.assertEqual(lines[1], 'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], 'alarm system,-,1234\n')

    file_object.close()

  def testReadlinesWithFileWithoutNewLineAtEnd(self):
    """Test reading lines from a file without a new line char at the end."""
    test_file = self._GetTestFilePath(['fls_bodyfile.txt'])
    self._SkipIfPathNotExists(test_file)

    test_file_path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_file_path_spec)
    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines()

    self.assertEqual(len(lines), 25)

  def testIterator(self):
    """Test the iterator functionality."""
    test_file = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_file)

    test_path_spec = os_path_spec.OSPathSpec(location=test_file)

    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_path_spec)
    text_file_object = text_file.TextFile(file_object)

    lines = []
    for line in text_file_object:
      lines.append(line)

    self.assertEqual(len(lines), 5)
    self.assertEqual(lines[0], 'place,user,password\n')
    self.assertEqual(lines[1], 'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], 'alarm system,-,1234\n')
    self.assertEqual(lines[3], 'treasure chest,-,1111\n')
    self.assertEqual(lines[4], 'uber secret laire,admin,admin\n')

    file_object.close()


if __name__ == '__main__':
  unittest.main()
