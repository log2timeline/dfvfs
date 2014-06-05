#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the file-like object implementation using pyewf."""

import unittest

from dfvfs.lib import ewf
from dfvfs.lib import definitions
from dfvfs.path import fake_path_spec
from dfvfs.path import ewf_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system


class GlobEwfFileTest(unittest.TestCase):
  """The unit test for the EWF image file glob functionality."""

  def _BuildFileFakeFileSystem(
      self, filename, number_of_segments, segment_file_path_specs):
    """Builds a fake file system containing EWF segment files.

    Args:
      filename: the filename of the first segment file with extension.
      number_of_segments: the number of segments.
      segment_file_path_specs: a list to store the segment file path
                               specifications in.

    Returns:
      The fake file system (instance of dvfvs.FakeFileSystem).
    """
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    filename, _, extension = filename.partition(u'.')
    number_of_segments += 1

    for segment_number in range(1, number_of_segments):
      if segment_number < 100:
        if extension[1] == u'x':
          path = u'/{0:s}.{1:s}x{2:02d}'.format(
              filename, extension[0], segment_number)
        else:
          path = u'/{0:s}.{1:s}{2:02d}'.format(
              filename, extension[0], segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)

        if extension[0].islower():
          third_letter = chr(ord('a') + remainder)
        else:
          third_letter = chr(ord('A') + remainder)

        segment_index, remainder = divmod(segment_index, 26)

        if extension[0].islower():
          second_letter = chr(ord('a') + remainder)
        else:
          second_letter = chr(ord('A') + remainder)

        first_letter = chr(ord(extension[0]) + segment_index)
        if extension[1] == u'x':
          path = u'/{0:s}.{1:s}x{2:s}{3:s}'.format(
              filename, first_letter, second_letter, third_letter)
        else:
          path = u'/{0:s}.{1:s}{2:s}{3:s}'.format(
              filename, first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      segment_file_path_specs.append(fake_path_spec.FakePathSpec(location=path))

    return file_system

  def testGlobE01(self):
    """Test the glob function."""
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.E01', 1, expected_segment_file_path_specs)

    # Test single segment file: E01.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: E01.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E10.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.E01', 10, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.E01', 100, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-EBA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.E01', 126, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-EZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.E01', 775, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-ZZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.E01', 14970, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-[ZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.E01', 14971, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)

  def testGlobEx01(self):
    """Test the glob function."""
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.Ex01', 1, expected_segment_file_path_specs)

    # Test single segment file: Ex01.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: Ex01.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex10.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.Ex01', 10, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.Ex01', 100, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ExBA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.Ex01', 126, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ExZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.Ex01', 775, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ZxZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.Ex01', 14970, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-[xZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.Ex01', 14971, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)

  def testGlobs01(self):
    """Test the glob function."""
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.s01', 1, expected_segment_file_path_specs)

    # Test single segment file: s01.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: s01.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s10.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.s01', 10, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.s01', 100, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-sba.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.s01', 126, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-szz.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.s01', 775, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-zzz.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.s01', 5506, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-[ZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        u'image.s01', 5507, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)


if __name__ == '__main__':
  unittest.main()
