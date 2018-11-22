#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the storage media RAW image support helper functions."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import raw
from dfvfs.path import fake_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system

from tests import test_lib as shared_test_lib


class GlobRawFileTest(shared_test_lib.BaseTestCase):
  """The unit test for the storage media RAW image file glob functionality."""

  def _BuildFileFakeFileSystem(
      self, segment_filenames, segment_file_path_specs):
    """Builds a fake file system containing storage media RAW segment files.

    Args:
      segment_filenames (list[str]): segment filenames.
      segment_file_path_specs (list[PathSpec]): resulting segment file path
          specifications.

    Returns:
      FakeFileSystem: fake file system.
    """
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    for segment_filename in segment_filenames:
      path = '/{0:s}'.format(segment_filename)

      file_system.AddFileEntry(path)
      segment_file_path_specs.append(fake_path_spec.FakePathSpec(location=path))

    return file_system

  def testGlobRawSinglecExtension(self):
    """Test the glob function for a RAW single extension scheme."""
    # Test single segment file: dd.
    segment_filenames = ['ímynd.dd']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/ímynd.dd')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test single segment file: dmg.
    segment_filenames = ['image.dmg']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.dmg')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test single segment file: img.
    segment_filenames = ['image.img']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.img')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test single segment file: raw.
    segment_filenames = ['image.raw']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.raw')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawAlphabeticalExtension(self):
    """Test the glob function for a RAW alphabetical extension scheme."""
    segment_filenames = ['image.aaa']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: aaa.
    path_spec = fake_path_spec.FakePathSpec(location='/image.aaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: aaa.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus.aaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: aaa-aak.
    segment_filenames = [
        'image.aaa', 'image.aab', 'image.aac', 'image.aad', 'image.aae',
        'image.aaf', 'image.aag', 'image.aah', 'image.aai', 'image.aaj',
        'image.aak']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.aaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: AAA-AAk.
    segment_filenames = [
        'image.AAA', 'image.AAB', 'image.AAC', 'image.AAD', 'image.AAE',
        'image.AAF', 'image.AAG', 'image.AAH', 'image.AAI', 'image.AAJ',
        'image.AAK']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.AAA')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawAlphabeticalSuffix(self):
    """Test the glob function for a RAW alphabetical suffix scheme."""
    segment_filenames = ['imageaaa']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: aaa.
    path_spec = fake_path_spec.FakePathSpec(location='/imageaaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: aaa.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogusaaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: aaa-aak.
    segment_filenames = [
        'imageaaa', 'imageaab', 'imageaac', 'imageaad', 'imageaae',
        'imageaaf', 'imageaag', 'imageaah', 'imageaai', 'imageaaj',
        'imageaak']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/imageaaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: AAA-AAk.
    segment_filenames = [
        'imageAAA', 'imageAAB', 'imageAAC', 'imageAAD', 'imageAAE',
        'imageAAF', 'imageAAG', 'imageAAH', 'imageAAI', 'imageAAJ',
        'imageAAK']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/imageAAA')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawNumericExtension(self):
    """Test the glob function for a RAW numeric extension scheme."""
    segment_filenames = ['image.000']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 000.
    path_spec = fake_path_spec.FakePathSpec(location='/image.000')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 000.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus.000')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 000-010.
    segment_filenames = [
        'image.000', 'image.001', 'image.002', 'image.003', 'image.004',
        'image.005', 'image.006', 'image.007', 'image.008', 'image.009',
        'image.010']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.000')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        'image.001', 'image.002', 'image.003', 'image.004', 'image.005',
        'image.006', 'image.007', 'image.008', 'image.009', 'image.010']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.001')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 1-10.
    segment_filenames = [
        'image.1', 'image.2', 'image.3', 'image.4', 'image.5',
        'image.6', 'image.7', 'image.8', 'image.9', 'image.10']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image.1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawNumericSuffix(self):
    """Test the glob function for a RAW numeric suffix scheme."""
    segment_filenames = ['image1']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 000.
    path_spec = fake_path_spec.FakePathSpec(location='/image1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 000.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 000-010.
    segment_filenames = [
        'image0', 'image1', 'image2', 'image3', 'image4', 'image5',
        'image6', 'image7', 'image8', 'image9', 'image10']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image0')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 1-10.
    segment_filenames = [
        'image1', 'image2', 'image3', 'image4', 'image5',
        'image6', 'image7', 'image8', 'image9', 'image10']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        'image001', 'image002', 'image003', 'image004', 'image005',
        'image006', 'image007', 'image008', 'image009', 'image010']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image001')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawAsbExtension(self):
    """Test the glob function for a RAW ASB extension scheme."""
    segment_filenames = ['image001.asb']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 001.
    path_spec = fake_path_spec.FakePathSpec(location='/image001.asb')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 001.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus000.asb')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        'image001.asb', 'image002.asb', 'image003.asb', 'image004.asb',
        'image005.asb', 'image006.asb', 'image007.asb', 'image008.asb',
        'image009.asb', 'image010.asb']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image001.asb')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawVMDKExtension(self):
    """Test the glob function for a RAW VMDK extension scheme."""
    segment_filenames = ['image-f001.vmdk']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 001.
    path_spec = fake_path_spec.FakePathSpec(location='/image-f001.vmdk')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 001.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location='/bogus-f000.vmdk')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        'image-f001.vmdk', 'image-f002.vmdk', 'image-f003.vmdk',
        'image-f004.vmdk', 'image-f005.vmdk', 'image-f006.vmdk',
        'image-f007.vmdk', 'image-f008.vmdk', 'image-f009.vmdk',
        'image-f010.vmdk']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location='/image-f001.vmdk')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)


if __name__ == '__main__':
  unittest.main()
