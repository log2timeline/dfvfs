#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the storage media RAW image support helper functions."""

import unittest

from dfvfs.lib import raw
from dfvfs.path import fake_path_spec
from dfvfs.path import raw_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system


class GlobRawFileTest(unittest.TestCase):
  """The unit test for the storage media RAW image file glob functionality."""

  def _BuildFileFakeFileSystem(
      self, segment_filenames, segment_file_path_specs):
    """Builds a fake file system containing storage media RAW segment files.

    Args:
      filename: the filename of the first segment file with extension.
      segment_filenames: a list of segment filenames.
      segment_file_path_specs: a list to store the segment file path
                               specifications in.

    Returns:
      The fake file system (instance of dvfvs.FakeFileSystem).
    """
    resolver_context = context.Context()
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    for segment_filename in segment_filenames:
      path = u'/{0:s}'.format(segment_filename)

      file_system.AddFileEntry(path)
      segment_file_path_specs.append(fake_path_spec.FakePathSpec(location=path))

    return file_system

  def testGlobRawSinglecExtension(self):
    """Test the glob function for a RAW single extension scheme."""
    # Test single segment file: dd.
    segment_filenames = [u'ímynd.dd']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/ímynd.dd')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test single segment file: dmg.
    segment_filenames = [u'image.dmg']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.dmg')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test single segment file: img.
    segment_filenames = [u'image.img']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.img')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test single segment file: raw.
    segment_filenames = [u'image.raw']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.raw')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawAlphabeticalExtension(self):
    """Test the glob function for a RAW alphabetical extension scheme."""
    segment_filenames = [u'image.aaa']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: aaa.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image.aaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: aaa.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus.aaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: aaa-aak.
    segment_filenames = [
        u'image.aaa', u'image.aab', u'image.aac', u'image.aad', u'image.aae',
        u'image.aaf', u'image.aag', u'image.aah', u'image.aai', u'image.aaj',
        u'image.aak']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.aaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: AAA-AAk.
    segment_filenames = [
        u'image.AAA', u'image.AAB', u'image.AAC', u'image.AAD', u'image.AAE',
        u'image.AAF', u'image.AAG', u'image.AAH', u'image.AAI', u'image.AAJ',
        u'image.AAK']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.AAA')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawAlphabeticalSuffix(self):
    """Test the glob function for a RAW alphabetical suffix scheme."""
    segment_filenames = [u'imageaaa']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: aaa.
    path_spec = fake_path_spec.FakePathSpec(location=u'/imageaaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: aaa.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogusaaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: aaa-aak.
    segment_filenames = [
        u'imageaaa', u'imageaab', u'imageaac', u'imageaad', u'imageaae',
        u'imageaaf', u'imageaag', u'imageaah', u'imageaai', u'imageaaj',
        u'imageaak']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/imageaaa')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: AAA-AAk.
    segment_filenames = [
        u'imageAAA', u'imageAAB', u'imageAAC', u'imageAAD', u'imageAAE',
        u'imageAAF', u'imageAAG', u'imageAAH', u'imageAAI', u'imageAAJ',
        u'imageAAK']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/imageAAA')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawNumericExtension(self):
    """Test the glob function for a RAW numeric extension scheme."""
    segment_filenames = [u'image.000']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 000.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image.000')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 000.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus.000')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 000-010.
    segment_filenames = [
        u'image.000', u'image.001', u'image.002', u'image.003', u'image.004',
        u'image.005', u'image.006', u'image.007', u'image.008', u'image.009',
        u'image.010']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.000')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        u'image.001', u'image.002', u'image.003', u'image.004', u'image.005',
        u'image.006', u'image.007', u'image.008', u'image.009', u'image.010']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.001')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 1-10.
    segment_filenames = [
        u'image.1', u'image.2', u'image.3', u'image.4', u'image.5',
        u'image.6', u'image.7', u'image.8', u'image.9', u'image.10']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image.1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawNumericSuffix(self):
    """Test the glob function for a RAW numeric suffix scheme."""
    segment_filenames = [u'image1']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 000.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 000.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 000-010.
    segment_filenames = [
        u'image0', u'image1', u'image2', u'image3', u'image4', u'image5',
        u'image6', u'image7', u'image8', u'image9', u'image10']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image0')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 1-10.
    segment_filenames = [
        u'image1', u'image2', u'image3', u'image4', u'image5',
        u'image6', u'image7', u'image8', u'image9', u'image10']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image1')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        u'image001', u'image002', u'image003', u'image004', u'image005',
        u'image006', u'image007', u'image008', u'image009', u'image010']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image001')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawAsbExtension(self):
    """Test the glob function for a RAW ASB extension scheme."""
    segment_filenames = [u'image001.asb']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 001.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image001.asb')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 001.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus000.asb')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        u'image001.asb', u'image002.asb', u'image003.asb', u'image004.asb',
        u'image005.asb', u'image006.asb', u'image007.asb', u'image008.asb',
        u'image009.asb', u'image010.asb']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image001.asb')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

  def testGlobRawVMDKExtension(self):
    """Test the glob function for a RAW VMDK extension scheme."""
    segment_filenames = [u'image-f001.vmdk']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    # Test single segment file: 001.
    path_spec = fake_path_spec.FakePathSpec(location=u'/image-f001.vmdk')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test non exiting segment file: 001.
    expected_segment_file_path_specs = []

    path_spec = fake_path_spec.FakePathSpec(location=u'/bogus-f000.vmdk')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)

    # Test multiple segment files: 001-010.
    segment_filenames = [
        u'image-f001.vmdk', u'image-f002.vmdk', u'image-f003.vmdk',
        u'image-f004.vmdk', u'image-f005.vmdk', u'image-f006.vmdk',
        u'image-f007.vmdk', u'image-f008.vmdk', u'image-f009.vmdk',
        u'image-f010.vmdk']
    expected_segment_file_path_specs = []
    file_system = self._BuildFileFakeFileSystem(
        segment_filenames, expected_segment_file_path_specs)

    path_spec = fake_path_spec.FakePathSpec(location=u'/image-f001.vmdk')
    path_spec = raw_path_spec.RawPathSpec(parent=path_spec)

    segment_file_path_specs = raw.RawGlobPathSpec(file_system, path_spec)
    self.assertEqual(
        len(segment_file_path_specs), len(expected_segment_file_path_specs))
    self.assertEqual(
        segment_file_path_specs, expected_segment_file_path_specs)


if __name__ == '__main__':
  unittest.main()
