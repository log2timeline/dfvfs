#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the text file interface for file-like objects."""

import os
import unittest

from dfvfs.file_io import os_file_io
from dfvfs.helpers import text_file
from dfvfs.path import os_path_spec
from dfvfs.resolver import context


# TODO: Add a test which tests reading a text file which is
# larger than the buffer size, and read lines until it crosses
# that original buffer size (to test if the buffer is correctly
# filled).
class TextFileTest(unittest.TestCase):
  """The unit test for the text file object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'another_file')
    self._os_path_spec1 = os_path_spec.OSPathSpec(location=test_file)

    test_file = os.path.join(u'test_data', u'password.txt')
    self._os_path_spec2 = os_path_spec.OSPathSpec(location=test_file)

  def testReadline(self):
    """Test the readline() function."""
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(self._os_path_spec1)
    text_file_object = text_file.TextFile(file_object)

    self.assertEqual(text_file_object.readline(), b'This is another file.\n')

    self.assertEqual(text_file_object.get_offset(), 22)

    file_object.close()

  def testReadlines(self):
    """Test the readlines() function."""
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(self._os_path_spec2)
    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines()

    self.assertEqual(len(lines), 5)
    self.assertEqual(lines[0], b'place,user,password\n')
    self.assertEqual(lines[1], b'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], b'alarm system,-,1234\n')
    self.assertEqual(lines[3], b'treasure chest,-,1111\n')
    self.assertEqual(lines[4], b'uber secret laire,admin,admin\n')

    file_object.close()

  def testReadlinesWithSizeHint(self):
    """Test the readlines() function."""
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(self._os_path_spec2)
    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines(sizehint=60)

    self.assertEqual(len(lines), 3)
    self.assertEqual(lines[0], b'place,user,password\n')
    self.assertEqual(lines[1], b'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], b'alarm system,-,1234\n')

    file_object.close()

  def testReadlinesWithFileWithoutNewLineAtEnd(self):
    """Test reading lines from a file without a new line char at the end."""
    test_file = os.path.join(u'test_data', u'fls_bodyfile.txt')
    test_file_path_spec = os_path_spec.OSPathSpec(location=test_file)
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(test_file_path_spec)
    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines()

    self.assertEqual(len(lines), 25)

  def testIterator(self):
    """Test the iterator functionality."""
    file_object = os_file_io.OSFile(self._resolver_context)
    file_object.open(self._os_path_spec2)
    text_file_object = text_file.TextFile(file_object)

    lines = []
    for line in text_file_object:
      lines.append(line)

    self.assertEqual(len(lines), 5)
    self.assertEqual(lines[0], b'place,user,password\n')
    self.assertEqual(lines[1], b'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], b'alarm system,-,1234\n')
    self.assertEqual(lines[3], b'treasure chest,-,1111\n')
    self.assertEqual(lines[4], b'uber secret laire,admin,admin\n')

    file_object.close()


if __name__ == '__main__':
  unittest.main()
