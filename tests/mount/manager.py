#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Virtual File System (VFS) mount point manager."""

import platform
import unittest

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.mount import manager
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests import test_lib as shared_test_lib


class MountPointManagerTest(shared_test_lib.BaseTestCase):
  """Class to test the mount point manager."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    test_path = self._GetTestFilePath(['ext2.qcow2'])
    self._SkipIfPathNotExists(test_path)

    self._resolver_context = context.Context()

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    self._qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)

  def testGetMountPoint(self):
    """Function to test the get mount point function."""
    manager.MountPointManager.RegisterMountPoint('C', self._qcow_path_spec)

    try:
      mount_point_path_spec = manager.MountPointManager.GetMountPoint('C')
      self.assertEqual(mount_point_path_spec, self._qcow_path_spec)

      mount_point_path_spec = manager.MountPointManager.GetMountPoint('D')
      self.assertIsNone(mount_point_path_spec)

    finally:
      manager.MountPointManager.DeregisterMountPoint('C')

  def testOpenFileObjectOnDirectory(self):
    """Function to test mount point resolving on a directory."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    if platform.system() == 'Windows':
      test_mounted_location = '\\file1.txt'
    else:
      test_mounted_location = '/file1.txt'

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    manager.MountPointManager.RegisterMountPoint(
        'testdir_os', test_os_path_spec)

    try:
      parent_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_MOUNT, identifier='testdir_os')
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=test_mounted_location,
          parent=parent_path_spec)
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)

      self.assertIsNotNone(file_object)
      self.assertEqual(file_object.get_size(), 6)

    finally:
      manager.MountPointManager.DeregisterMountPoint('testdir_os')

  def testOpenFileObjectOnImage(self):
    """Function to test mount point resolving on a storage media image."""
    manager.MountPointManager.RegisterMountPoint('C', self._qcow_path_spec)

    try:
      parent_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_MOUNT, identifier='C')
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.PREFERRED_EXT_BACK_END, location='/passwords.txt',
          parent=parent_path_spec)
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)

      self.assertIsNotNone(file_object)
      self.assertEqual(file_object.get_size(), 116)

      parent_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_MOUNT, identifier='D')
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.PREFERRED_EXT_BACK_END, location='/passwords.txt',
          parent=parent_path_spec)

      with self.assertRaises(errors.MountPointError):
        file_object = resolver.Resolver.OpenFileObject(
            path_spec, resolver_context=self._resolver_context)

    finally:
      manager.MountPointManager.DeregisterMountPoint('C')


if __name__ == '__main__':
  unittest.main()
