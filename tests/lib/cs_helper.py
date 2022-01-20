#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the helper functions for Core Storage (CS) support."""

import unittest

from dfvfs.lib import cs_helper
from dfvfs.path import cs_path_spec
from dfvfs.path import fake_path_spec

from tests import test_lib as shared_test_lib


class CSHelperTest(shared_test_lib.BaseTestCase):
  """Tests for the helper functions for Core Storage (CS) support."""

  def testCSPathSpecGetVolumeIndex(self):
    """Tests the CSPathSpecGetVolumeIndex function."""
    test_fake_path_spec = fake_path_spec.FakePathSpec(location='/')

    path_spec = cs_path_spec.CSPathSpec(
        parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)

    path_spec = cs_path_spec.CSPathSpec(
        location='/cs2', parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = cs_path_spec.CSPathSpec(
        volume_index=1, parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = cs_path_spec.CSPathSpec(
        location='/cs2', volume_index=1, parent=test_fake_path_spec)

    self.assertIsNotNone(path_spec)

    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)
    self.assertEqual(volume_index, 1)

    path_spec = cs_path_spec.CSPathSpec(
        location='/cs', parent=test_fake_path_spec)

    volume_index = cs_helper.CSPathSpecGetVolumeIndex(path_spec)
    self.assertIsNone(volume_index)


if __name__ == '__main__':
  unittest.main()
