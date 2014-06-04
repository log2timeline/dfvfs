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

  def testGlobE01(self):
    """Test the glob function."""
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)
    file_system.AddFileEntry(u'/image.E01')

    # Test single segment file: E01.
    expected_segment_file_path_specs = [
        fake_path_spec.FakePathSpec(location=u'/image.E01')]

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
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
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 11):
      path = u'/image.E{0:02d}'.format(segment_number)
      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 101):
      if segment_number < 100:
        path = u'/image.E{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        second_letter = chr(ord('A') + segment_index)
        path = u'/image.E{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-EBA.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 127):
      if segment_number < 100:
        path = u'/image.E{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        second_letter = chr(ord('A') + segment_index)
        path = u'/image.E{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-EZZ.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 776):
      if segment_number < 100:
        path = u'/image.E{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        second_letter = chr(ord('A') + segment_index)
        path = u'/image.E{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-ZZZ.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 14971):
      if segment_number < 100:
        path = u'/image.E{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        segment_index, remainder = divmod(segment_index, 26)
        second_letter = chr(ord('A') + remainder)
        first_letter = chr(ord('E') + segment_index)
        path = u'/image.{0:s}{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-[ZZ.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 14972):
      if segment_number < 100:
        path = u'/image.E{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        segment_index, remainder = divmod(segment_index, 26)
        second_letter = chr(ord('A') + remainder)
        first_letter = chr(ord('E') + segment_index)
        path = u'/image.{0:s}{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.E01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)

  def testGlobEx01(self):
    """Test the glob function."""
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)
    file_system.AddFileEntry(u'/image.Ex01')

    # Test single segment file: Ex01.
    expected_segment_file_path_specs = [
        fake_path_spec.FakePathSpec(location=u'/image.Ex01')]

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
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
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 11):
      path = u'/image.Ex{0:02d}'.format(segment_number)
      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 101):
      if segment_number < 100:
        path = u'/image.Ex{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        second_letter = chr(ord('A') + segment_index)
        path = u'/image.Ex{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ExBA.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 127):
      if segment_number < 100:
        path = u'/image.Ex{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        second_letter = chr(ord('A') + segment_index)
        path = u'/image.Ex{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ExZZ.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 776):
      if segment_number < 100:
        path = u'/image.Ex{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        second_letter = chr(ord('A') + segment_index)
        path = u'/image.Ex{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ZxZZ.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 14971):
      if segment_number < 100:
        path = u'/image.Ex{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        segment_index, remainder = divmod(segment_index, 26)
        second_letter = chr(ord('A') + remainder)
        first_letter = chr(ord('E') + segment_index)
        path = u'/image.{0:s}x{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-[xZZ.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 14972):
      if segment_number < 100:
        path = u'/image.Ex{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('A') + remainder)
        segment_index, remainder = divmod(segment_index, 26)
        second_letter = chr(ord('A') + remainder)
        first_letter = chr(ord('E') + segment_index)
        path = u'/image.{0:s}x{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.Ex01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)

  def testGlobs01(self):
    """Test the glob function."""
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)
    file_system.AddFileEntry(u'/image.s01')

    # Test single segment file: s01.
    expected_segment_file_path_specs = [
        fake_path_spec.FakePathSpec(location=u'/image.s01')]

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
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
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 11):
      path = u'/image.s{0:02d}'.format(segment_number)
      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 101):
      if segment_number < 100:
        path = u'/image.s{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('a') + remainder)
        second_letter = chr(ord('a') + segment_index)
        path = u'/image.s{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-sba.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 127):
      if segment_number < 100:
        path = u'/image.s{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('a') + remainder)
        second_letter = chr(ord('a') + segment_index)
        path = u'/image.s{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-szz.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 776):
      if segment_number < 100:
        path = u'/image.s{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('a') + remainder)
        second_letter = chr(ord('a') + segment_index)
        path = u'/image.s{0:s}{1:s}'.format(second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-zzz.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 5507):
      if segment_number < 100:
        path = u'/image.s{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('a') + remainder)
        segment_index, remainder = divmod(segment_index, 26)
        second_letter = chr(ord('a') + remainder)
        first_letter = chr(ord('s') + segment_index)
        path = u'/image.{0:s}{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    self.assertEquals(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEquals(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-[ZZ.
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    file_system.AddFileEntry(
        u'/', file_entry_type=definitions.FILE_ENTRY_TYPE_DIRECTORY)

    expected_segment_file_path_specs = []

    for segment_number in range(1, 5508):
      if segment_number < 100:
        path = u'/image.s{0:02d}'.format(segment_number)
      else:
        segment_index = segment_number - 100
        segment_index, remainder = divmod(segment_index, 26)
        third_letter = chr(ord('a') + remainder)
        segment_index, remainder = divmod(segment_index, 26)
        second_letter = chr(ord('a') + remainder)
        first_letter = chr(ord('s') + segment_index)
        path = u'/image.{0:s}{1:s}{2:s}'.format(
            first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      expected_segment_file_path_specs.append(
          fake_path_spec.FakePathSpec(location=path))

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.s01')
    path_spec = ewf_path_spec.EwfPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)


if __name__ == '__main__':
  unittest.main()
