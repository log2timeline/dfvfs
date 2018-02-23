#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the resolver context object."""

from __future__ import unicode_literals

import unittest

from dfvfs.file_io import fake_file_io
from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import fake_file_system


class ContextTest(unittest.TestCase):
  """Tests for the resolver context object."""

  def testCacheFileObject(self):
    """Tests the cache file-like object functionality."""
    resolver_context = context.Context()

    # pylint: disable=protected-access
    self.assertEqual(len(resolver_context._file_object_cache._values), 0)

    path_spec = fake_path_spec.FakePathSpec(location='/empty.txt')
    file_object = fake_file_io.FakeFile(resolver_context, b'')

    resolver_context.CacheFileObject(path_spec, file_object)
    self.assertEqual(len(resolver_context._file_object_cache._values), 1)

    cached_object = resolver_context.GetFileObject(path_spec)
    self.assertEqual(cached_object, file_object)

    resolver_context.GrabFileObject(path_spec)
    self.assertEqual(len(resolver_context._file_object_cache._values), 1)

    resolver_context.GrabFileObject(path_spec)
    self.assertEqual(len(resolver_context._file_object_cache._values), 1)

    resolver_context.ReleaseFileObject(file_object)
    self.assertEqual(len(resolver_context._file_object_cache._values), 1)

    resolver_context.ReleaseFileObject(file_object)
    self.assertEqual(len(resolver_context._file_object_cache._values), 0)

  def testCacheFileSystem(self):
    """Tests the cache file system object functionality."""
    resolver_context = context.Context()

    # pylint: disable=protected-access
    self.assertEqual(len(resolver_context._file_system_cache._values), 0)

    path_spec = fake_path_spec.FakePathSpec(location='/')
    file_system = fake_file_system.FakeFileSystem(resolver_context)

    resolver_context.CacheFileSystem(path_spec, file_system)
    self.assertEqual(len(resolver_context._file_system_cache._values), 1)

    cached_object = resolver_context.GetFileSystem(path_spec)
    self.assertEqual(cached_object, file_system)

    resolver_context.GrabFileSystem(path_spec)
    self.assertEqual(len(resolver_context._file_system_cache._values), 1)

    resolver_context.GrabFileSystem(path_spec)
    self.assertEqual(len(resolver_context._file_system_cache._values), 1)

    resolver_context.ReleaseFileSystem(file_system)
    self.assertEqual(len(resolver_context._file_system_cache._values), 1)

    resolver_context.ReleaseFileSystem(file_system)
    self.assertEqual(len(resolver_context._file_system_cache._values), 0)


if __name__ == '__main__':
  unittest.main()
