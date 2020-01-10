#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the EWF image support helper functions."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import ewf
from dfvfs.path import fake_path_spec
from dfvfs.path import ewf_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system

from tests import test_lib as shared_test_lib


class GlobEWFFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the EWF image file glob functionality."""

  def _BuildFileFakeFileSystem(
      self, filename, number_of_segments, segment_file_path_specs):
    """Builds a fake file system containing EWF segment files.

    Args:
      filename (str): filename of the first segment file with extension.
      number_of_segments (int): number of segments.
      segment_file_path_specs (list[PathSpec]): resulting segment file path
          specifications.

    Returns:
      FakeFileSystem: fake file system.
    """
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    filename, _, extension = filename.partition('.')
    number_of_segments += 1

    for segment_number in range(1, number_of_segments):
      if segment_number < 100:
        if extension[1] == 'x':
          path = '/{0:s}.{1:s}x{2:02d}'.format(
              filename, extension[0], segment_number)
        else:
          path = '/{0:s}.{1:s}{2:02d}'.format(
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
        if extension[1] == 'x':
          path = '/{0:s}.{1:s}x{2:s}{3:s}'.format(
              filename, first_letter, second_letter, third_letter)
        else:
          path = '/{0:s}.{1:s}{2:s}{3:s}'.format(
              filename, first_letter, second_letter, third_letter)

      file_system.AddFileEntry(path)
      path_spec = fake_path_spec.FakePathSpec(location=path)
      segment_file_path_specs.append(path_spec)

    return file_system

  def testGlobE01(self):
    """Test the glob function."""
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'ext2.E01', 1, expected_segment_file_path_specs)

    # Test single segment file: E01.
    path_spec = fake_path_spec.FakePathSpec(location='/ext2.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: E01.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E10.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'ext2.E01', 10, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/ext2.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'ext2.E01', 100, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/ext2.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-EBA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'ext2.E01', 126, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/ext2.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-EZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'ext2.E01', 775, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/ext2.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-ZZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'ext2.E01', 14970, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/ext2.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-[ZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'ext2.E01', 14971, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/ext2.E01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)

  def testGlobEx01(self):
    """Test the glob function."""
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.Ex01', 1, expected_segment_file_path_specs)

    # Test single segment file: Ex01.
    path_spec = fake_path_spec.FakePathSpec(location='/image.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: Ex01.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex10.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.Ex01', 10, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.Ex01', 100, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ExBA.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.Ex01', 126, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ExZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.Ex01', 775, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-ZxZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.Ex01', 14970, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: Ex01-Ex99,ExAA-[xZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.Ex01', 14971, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.Ex01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)

  def testGlobs01(self):
    """Test the glob function."""
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.s01', 1, expected_segment_file_path_specs)

    # Test single segment file: s01.
    path_spec = fake_path_spec.FakePathSpec(location='/image.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: s01.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s10.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.s01', 10, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.s01', 100, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-sba.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.s01', 126, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-szz.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.s01', 775, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: s01-s99,saa-zzz.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.s01', 5506, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: E01-E99,EAA-[ZZ.
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        'image.s01', 5507, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.s01')
    path_spec = ewf_path_spec.EWFPathSpec(parent=path_spec)

    with self.assertRaises(RuntimeError):
      segment_file_path_specs = ewf.EWFGlobPathSpec(file_system, path_spec)


if __name__ == '__main__':
  unittest.main()
