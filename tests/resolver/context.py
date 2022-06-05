#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the resolver context object."""

import platform
import unittest

from dfvfs.file_io import fake_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver
from dfvfs.vfs import fake_file_system

from tests import test_lib as shared_test_lib


class ContextTest(shared_test_lib.BaseTestCase):
  """Tests for the resolver context object."""

  # pylint: disable=protected-access

  def testCacheFileObject(self):
    """Tests the cache file-like object functionality."""
    resolver_context = context.Context()

    self.assertEqual(len(resolver_context._file_object_cache), 0)

    path_spec = fake_path_spec.FakePathSpec(location='/empty.txt')
    file_object = fake_file_io.FakeFile(resolver_context, path_spec, b'')

    resolver_context.CacheFileObject(path_spec, file_object)
    self.assertEqual(len(resolver_context._file_object_cache), 1)

    cached_object = resolver_context.GetFileObject(path_spec)
    self.assertEqual(cached_object, file_object)

  def testCacheFileSystem(self):
    """Tests the cache file system object functionality."""
    resolver_context = context.Context()

    self.assertEqual(len(resolver_context._file_system_cache), 0)

    path_spec = fake_path_spec.FakePathSpec(location='/')
    file_system = fake_file_system.FakeFileSystem(resolver_context, path_spec)

    resolver_context.CacheFileSystem(path_spec, file_system)
    self.assertEqual(len(resolver_context._file_system_cache), 1)

    cached_object = resolver_context.GetFileSystem(path_spec)
    self.assertEqual(cached_object, file_system)

  def testGetMountPoint(self):
    """Tests the GetMountPoint function."""
    test_path = self._GetTestFilePath(['ext2.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)

    resolver_context = context.Context()
    resolver_context.RegisterMountPoint('C', test_qcow_path_spec)

    try:
      mount_point_path_spec = resolver_context.GetMountPoint('C')
      self.assertEqual(mount_point_path_spec, test_qcow_path_spec)

      mount_point_path_spec = resolver_context.GetMountPoint('D')
      self.assertIsNone(mount_point_path_spec)

    finally:
      resolver_context.DeregisterMountPoint('C')

  def testOpenFileObjectOnDirectory(self):
    """Tests mount point resolving on a directory."""
    test_path = self._GetTestFilePath(['testdir_os'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)

    resolver_context = context.Context()
    resolver_context.RegisterMountPoint('testdir_os', test_os_path_spec)

    if platform.system() == 'Windows':
      test_mounted_location = '\\file1.txt'
    else:
      test_mounted_location = '/file1.txt'

    try:
      parent_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_MOUNT, identifier='testdir_os')
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=test_mounted_location,
          parent=parent_path_spec)
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=resolver_context)

      self.assertIsNotNone(file_object)
      self.assertEqual(file_object.get_size(), 6)

    finally:
      resolver_context.DeregisterMountPoint('testdir_os')

  def testOpenFileObjectOnImage(self):
    """Tests mount point resolving on a storage media image."""
    test_path = self._GetTestFilePath(['ext2.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)

    resolver_context = context.Context()
    resolver_context.RegisterMountPoint('C', test_qcow_path_spec)

    try:
      parent_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_MOUNT, identifier='C')
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.PREFERRED_EXT_BACK_END, location='/passwords.txt',
          parent=parent_path_spec)
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=resolver_context)

      self.assertIsNotNone(file_object)
      self.assertEqual(file_object.get_size(), 116)

      parent_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_MOUNT, identifier='D')
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.PREFERRED_EXT_BACK_END, location='/passwords.txt',
          parent=parent_path_spec)

      with self.assertRaises(errors.MountPointError):
        file_object = resolver.Resolver.OpenFileObject(
            path_spec, resolver_context=resolver_context)

    finally:
      resolver_context.DeregisterMountPoint('C')


if __name__ == '__main__':
  unittest.main()
