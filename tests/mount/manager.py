#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Virtual File System (VFS) mount point manager."""

from __future__ import unicode_literals

import unittest

from dfvfs.lib import errors
from dfvfs.mount import manager
from dfvfs.path import mount_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests import test_lib as shared_test_lib


class MountPointManagerTest(shared_test_lib.BaseTestCase):
  """Class to test the mount point manager."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = self._GetTestFilePath(['ext2.qcow2'])
    self._SkipIfPathNotExists(test_file)

    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

  def testGetMountPoint(self):
    """Function to test the get mount point function."""
    manager.MountPointManager.RegisterMountPoint('C', self._qcow_path_spec)

    mount_point_path_spec = manager.MountPointManager.GetMountPoint('C')
    self.assertEqual(mount_point_path_spec, self._qcow_path_spec)

    mount_point_path_spec = manager.MountPointManager.GetMountPoint('D')
    self.assertIsNone(mount_point_path_spec)

    manager.MountPointManager.DeregisterMountPoint('C')

  def testOpenFileObject(self):
    """Function to test mount point resolving."""
    manager.MountPointManager.RegisterMountPoint('C', self._qcow_path_spec)

    parent_path_spec = mount_path_spec.MountPathSpec(identifier='C')
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/passwords.txt', parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    self.assertIsNotNone(file_object)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    parent_path_spec = mount_path_spec.MountPathSpec(identifier='D')
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/passwords.txt', parent=parent_path_spec)

    with self.assertRaises(errors.MountPointError):
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)

    manager.MountPointManager.DeregisterMountPoint('C')


if __name__ == '__main__':
  unittest.main()
