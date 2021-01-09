#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the resolver objects cache."""

import unittest

from dfvfs.lib import errors
from dfvfs.path import fake_path_spec
from dfvfs.resolver import cache


class TestVFSObject(object):
  """Test VFS object."""


class ObjectsCacheTest(unittest.TestCase):
  """Tests for the resolver objects cache."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._path_spec = fake_path_spec.FakePathSpec(location='1')
    self._vfs_object = TestVFSObject()

  def testCache(self):
    """Tests the cache functionality."""
    cache_object = cache.ObjectsCache(1)
    self.assertIsNotNone(cache_object)

    # pylint: disable=protected-access
    self.assertEqual(len(cache_object._values), 0)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)
    self.assertEqual(len(cache_object._values), 1)

    with self.assertRaises(KeyError):
      cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)
    self.assertEqual(len(cache_object._values), 1)

    cache_object.RemoveObject(self._path_spec.comparable)
    self.assertEqual(len(cache_object._values), 0)

  def testCacheFull(self):
    """Tests if the CacheFullError is raised."""
    cache_object = cache.ObjectsCache(1)
    self.assertIsNotNone(cache_object)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)

    path_spec = fake_path_spec.FakePathSpec(location='2')
    vfs_object = TestVFSObject()

    with self.assertRaises(errors.CacheFullError):
      cache_object.CacheObject(path_spec.comparable, vfs_object)

  def testEmpty(self):
    """Tests the Empty method."""
    cache_object = cache.ObjectsCache(5)
    self.assertIsNotNone(cache_object)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)

    path_spec = fake_path_spec.FakePathSpec(location='2')
    vfs_object = TestVFSObject()
    cache_object.CacheObject(path_spec.comparable, vfs_object)

    path_spec = fake_path_spec.FakePathSpec(location='3')
    vfs_object = TestVFSObject()
    cache_object.CacheObject(path_spec.comparable, vfs_object)

    # pylint: disable=protected-access
    self.assertEqual(len(cache_object._values), 3)

    cache_object.Empty()
    self.assertEqual(len(cache_object._values), 0)

  def testGetObject(self):
    """Tests the GetObject method."""
    cache_object = cache.ObjectsCache(1)
    self.assertIsNotNone(cache_object)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)

    cached_object = cache_object.GetObject(self._path_spec.comparable)
    self.assertEqual(cached_object, self._vfs_object)


if __name__ == '__main__':
  unittest.main()
