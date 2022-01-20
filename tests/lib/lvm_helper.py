#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the helper functions for Logical Volume Manager (LVM) support."""

import unittest

from dfvfs.lib import lvm_helper
from dfvfs.path import lvm_path_spec
from dfvfs.path import fake_path_spec

from tests import test_lib as shared_test_lib


class LVMHelperTest(shared_test_lib.BaseTestCase):
  """Tests for the helper functions for Logical Volume Manager (LVM) support."""

  def testLVMPathSpecGetVolumeIndex(self):
    """Tests the LVMPathSpecGetVolumeIndex function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')

    path_spec = lvm_path_spec.LVMPathSpec(
        parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = lvm_helper.LVMPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm2', parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = lvm_helper.LVMPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = lvm_path_spec.LVMPathSpec(
        volume_index=1, parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = lvm_helper.LVMPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm2', volume_index=1, parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = lvm_helper.LVMPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = lvm_path_spec.LVMPathSpec(
        location='/lvm', parent=test_fake_path_spec)

    volume_index = lvm_helper.LVMPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)


if __name__ == '__main__':
  unittest.main()
