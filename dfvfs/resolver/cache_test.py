#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the resolver objects cache."""

import unittest

from dfvfs.lib import errors
from dfvfs.path import fake_path_spec
from dfvfs.resolver import cache


class TestVFSObject(object):
  """Class to define the test VFS object."""


class ObjectsCacheValueTest(unittest.TestCase):
  """Tests for the resolver objects cache value."""

  def testReferenceCount(self):
    """Tests the reference count functionality."""
    vfs_object = TestVFSObject()

    cache_value = cache.ObjectsCacheValue(vfs_object)
    self.assertNotEquals(cache_value, None)

    # pylint: disable=protected-access
    self.assertEquals(cache_value._reference_count, 0)

    self.assertTrue(cache_value.IsDereferenced())

    cache_value.IncrementReferenceCount()
    self.assertEquals(cache_value._reference_count, 1)

    self.assertFalse(cache_value.IsDereferenced())

    cache_value.IncrementReferenceCount()
    self.assertEquals(cache_value._reference_count, 2)

    cache_value.DecrementReferenceCount()
    self.assertEquals(cache_value._reference_count, 1)

    cache_value.DecrementReferenceCount()
    self.assertEquals(cache_value._reference_count, 0)

    self.assertTrue(cache_value.IsDereferenced())

    with self.assertRaises(RuntimeError):
      cache_value.DecrementReferenceCount()


class ObjectsCacheTest(unittest.TestCase):
  """Tests for the resolver objects cache."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._path_spec = fake_path_spec.FakePathSpec(location=u'1')
    self._vfs_object = TestVFSObject()

  def testCache(self):
    """Tests the cache functionality."""
    cache_object = cache.ObjectsCache(1)
    self.assertNotEquals(cache_object, None)

    # pylint: disable=protected-access
    self.assertEquals(len(cache_object._values), 0)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)
    self.assertEquals(len(cache_object._values), 1)

    with self.assertRaises(KeyError):
      cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)
    self.assertEquals(len(cache_object._values), 1)

    cache_object.RemoveObject(self._path_spec.comparable)
    self.assertEquals(len(cache_object._values), 0)

  def testCacheFull(self):
    """Tests if the CacheFullError is raised."""
    cache_object = cache.ObjectsCache(1)
    self.assertNotEquals(cache_object, None)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)

    path_spec = fake_path_spec.FakePathSpec(location=u'2')
    vfs_object = TestVFSObject()

    with self.assertRaises(errors.CacheFullError):
      cache_object.CacheObject(path_spec.comparable, vfs_object)

  def testEmpty(self):
    """Tests the Empty method."""
    cache_object = cache.ObjectsCache(5)
    self.assertNotEquals(cache_object, None)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)

    path_spec = fake_path_spec.FakePathSpec(location=u'2')
    vfs_object = TestVFSObject()
    cache_object.CacheObject(path_spec.comparable, vfs_object)

    path_spec = fake_path_spec.FakePathSpec(location=u'3')
    vfs_object = TestVFSObject()
    cache_object.CacheObject(path_spec.comparable, vfs_object)

    # pylint: disable=protected-access
    self.assertEquals(len(cache_object._values), 3)

    cache_object.Empty()
    self.assertEquals(len(cache_object._values), 0)

  def testGetObject(self):
    """Tests the GetObject method."""
    cache_object = cache.ObjectsCache(1)
    self.assertNotEquals(cache_object, None)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)

    cached_object = cache_object.GetObject(self._path_spec.comparable)
    self.assertEquals(cached_object, self._vfs_object)

  def testGetCacheValueByObjectGetCacheValueByObject(self):
    """Tests the GetCacheValueByObject method."""
    cache_object = cache.ObjectsCache(1)
    self.assertNotEquals(cache_object, None)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)

    identifier, cache_value = cache_object.GetCacheValueByObject(
        self._vfs_object)
    self.assertEquals(identifier, self._path_spec.comparable)
    self.assertEquals(cache_value.vfs_object, self._vfs_object)

  def testGrabAndRelease(self):
    """Tests the GrabObject and ReleaseObject methods."""
    cache_object = cache.ObjectsCache(1)
    self.assertNotEquals(cache_object, None)

    cache_object.CacheObject(self._path_spec.comparable, self._vfs_object)
    _, cache_value = cache_object.GetCacheValueByObject(self._vfs_object)
    # pylint: disable=protected-access
    self.assertEquals(cache_value._reference_count, 0)

    cache_object.GrabObject(self._path_spec.comparable)
    _, cache_value = cache_object.GetCacheValueByObject(self._vfs_object)
    self.assertEquals(cache_value._reference_count, 1)

    cache_object.GrabObject(self._path_spec.comparable)
    _, cache_value = cache_object.GetCacheValueByObject(self._vfs_object)
    self.assertEquals(cache_value._reference_count, 2)

    cache_object.ReleaseObject(self._path_spec.comparable)
    _, cache_value = cache_object.GetCacheValueByObject(self._vfs_object)
    self.assertEquals(cache_value._reference_count, 1)

    cache_object.ReleaseObject(self._path_spec.comparable)
    _, cache_value = cache_object.GetCacheValueByObject(self._vfs_object)
    self.assertEquals(cache_value._reference_count, 0)


if __name__ == '__main__':
  unittest.main()
