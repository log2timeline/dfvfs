#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the TSK partition path specification implementation."""

import unittest

from dfvfs.path import tsk_partition_path_spec

from tests.path import test_lib


class TSKPartitionPathSpecTest(test_lib.PathSpecTestCase):
  """Tests for the TSK partition path specification implementation."""

  def testInitialize(self):
    """Tests the path specification initialization."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        start_offset=0x2000, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', part_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    with self.assertRaises(ValueError):
      _ = tsk_partition_path_spec.TSKPartitionPathSpec(parent=None)

    with self.assertRaises(ValueError):
      _ = tsk_partition_path_spec.TSKPartitionPathSpec(
          parent=self._path_spec, bogus=u'BOGUS')

  def testComparable(self):
    """Tests the path specification comparable property."""
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: TSK_PARTITION',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: TSK_PARTITION, location: /p2',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: TSK_PARTITION, part index: 1',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        start_offset=0x2000, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: TSK_PARTITION, start offset: 0x00002000',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', part_index=1, parent=self._path_spec)

    self.assertIsNotNone(path_spec)

    expected_comparable = u'\n'.join([
        u'type: TEST',
        u'type: TSK_PARTITION, location: /p2, part index: 1',
        u''])

    self.assertEqual(path_spec.comparable, expected_comparable)


if __name__ == '__main__':
  unittest.main()
