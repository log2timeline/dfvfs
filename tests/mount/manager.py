#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Virtual File System (VFS) mount point manager."""

import os
import unittest

from dfvfs.lib import errors
from dfvfs.mount import manager
from dfvfs.path import mount_path_spec
from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver


class MountPointManagerTest(unittest.TestCase):
  """Class to test the mount point manager."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'image.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QCOWPathSpec(parent=path_spec)

  def testGetMountPoint(self):
    """Function to test the get mount point function."""
    manager.MountPointManager.RegisterMountPoint(u'C', self._qcow_path_spec)

    mount_point_path_spec = manager.MountPointManager.GetMountPoint(u'C')
    self.assertEqual(mount_point_path_spec, self._qcow_path_spec)

    mount_point_path_spec = manager.MountPointManager.GetMountPoint(u'D')
    self.assertIsNone(mount_point_path_spec)

    manager.MountPointManager.DeregisterMountPoint(u'C')

  def testOpenFileObject(self):
    """Function to test mount point resolving."""
    manager.MountPointManager.RegisterMountPoint(u'C', self._qcow_path_spec)

    parent_path_spec = mount_path_spec.MountPathSpec(identifier=u'C')
    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/passwords.txt', parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    self.assertIsNotNone(file_object)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    parent_path_spec = mount_path_spec.MountPathSpec(identifier=u'D')
    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/passwords.txt', parent=parent_path_spec)

    with self.assertRaises(errors.MountPointError):
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)

    manager.MountPointManager.DeregisterMountPoint(u'C')


if __name__ == '__main__':
  unittest.main()
