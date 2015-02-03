# -*- coding: utf-8 -*-
"""Shared test cases."""

import unittest

from dfvfs.lib import errors
from dfvfs.resolver import context
from dfvfs.resolver import resolver_helper


class TestResolverHelper(resolver_helper.ResolverHelper):
  """Test resolver helper."""

  TYPE_INDICATOR = u'TEST'

  def __init__(self, **kwargs):
    """Initializes the resolver helper object."""
    super(TestResolverHelper, self).__init__(parent=None, **kwargs)

  def OpenFileObject(self, unused_path_spec, unused_resolver_context):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO) or None if the path
      specification could not be resolved.
    """
    return


class ResolverHelperTestCase(unittest.TestCase):
  """The unit test case for resolver helper implementions."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def _TestOpenFileObject(self, resolver_helper_object, path_spec):
    """Tests the OpenFileObject function.

    Args:
      resolver_helper_object: the resolver helper object (instance of
                              resolver.ResolverHelper).
      path_spec: the VFS path specification (instance of path.PathSpec).
    """
    file_object = resolver_helper_object.OpenFileObject(
        path_spec, self._resolver_context)

    self.assertNotEquals(file_object, None)

    file_object.close()

  def _TestOpenFileSystem(self, resolver_helper_object, path_spec):
    """Tests the OpenFileSystem function.

    Args:
      resolver_helper_object: the resolver helper object (instance of
                              resolver.ResolverHelper).
      path_spec: the VFS path specification (instance of path.PathSpec).
    """
    file_system = resolver_helper_object.OpenFileSystem(
        path_spec, self._resolver_context)

    self.assertNotEquals(file_system, None)

  def _TestOpenFileSystemRaises(self, resolver_helper_object, path_spec):
    """Tests if the OpenFileSystem function raises errors.PathSpecError.

    Args:
      resolver_helper_object: the resolver helper object (instance of
                              resolver.ResolverHelper).
      path_spec: the VFS path specification (instance of path.PathSpec).
    """
    with self.assertRaises(errors.PathSpecError):
      _ = resolver_helper_object.OpenFileSystem(
          path_spec, self._resolver_context)
