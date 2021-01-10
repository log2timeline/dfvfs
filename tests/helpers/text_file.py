#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the text file interface for file-like objects."""

import unittest

from dfvfs.helpers import text_file
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

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
    test_path = self._GetTestFilePath(['another_file'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

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

  def testReadlineWithError(self):
    """Test the readline() function with an encoding error."""
    test_path = self._GetTestFilePath(['another_file_with_error'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

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

  def testReadlineUTF16(self):
    """Test the readline() function on UTF-16 encoded text."""
    test_path = self._GetTestFilePath(['another_file.utf16'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

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

  def testReadlineMultipleLines(self):
    """Test the readline() function on multiple lines."""
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

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

  def testReadlineWithEndOfFileTruncation(self):
    """Test the readline() function with specified size at end of file."""
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

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

  def testReadlines(self):
    """Test the readlines() function."""
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines()

    self.assertEqual(len(lines), 5)
    self.assertEqual(lines[0], 'place,user,password\n')
    self.assertEqual(lines[1], 'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], 'alarm system,-,1234\n')
    self.assertEqual(lines[3], 'treasure chest,-,1111\n')
    self.assertEqual(lines[4], 'uber secret laire,admin,admin\n')

  def testReadlinesWithSizeHint(self):
    """Test the readlines() function."""
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines(sizehint=60)

    self.assertEqual(len(lines), 3)
    self.assertEqual(lines[0], 'place,user,password\n')
    self.assertEqual(lines[1], 'bank,joesmith,superrich\n')
    self.assertEqual(lines[2], 'alarm system,-,1234\n')

  def testReadlinesWithFileWithoutNewLineAtEnd(self):
    """Test reading lines from a file without a new line char at the end."""
    test_path = self._GetTestFilePath(['fls_bodyfile.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

    text_file_object = text_file.TextFile(file_object)

    lines = text_file_object.readlines()

    self.assertEqual(len(lines), 25)

  def testIterator(self):
    """Test the iterator functionality."""
    test_path = self._GetTestFilePath(['password.txt'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    file_object = resolver.Resolver.OpenFileObject(
        test_os_path_spec, resolver_context=self._resolver_context)

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


if __name__ == '__main__':
  unittest.main()
