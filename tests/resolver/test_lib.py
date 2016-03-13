# -*- coding: utf-8 -*-
"""Shared test cases."""

import unittest

from dfvfs.resolver import context
from dfvfs.resolver import resolver_helper


class TestResolverHelper(resolver_helper.ResolverHelper):
  """Test resolver helper."""

  TYPE_INDICATOR = u'TEST'

  def __init__(self, **kwargs):
    """Initializes the resolver helper object."""
    super(TestResolverHelper, self).__init__(parent=None, **kwargs)

  def NewFileObject(self, unused_resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of FileIO).
    """
    return


class ResolverHelperTestCase(unittest.TestCase):
  """The unit test case for resolver helper implementions."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def _TestNewFileObject(self, resolver_helper_object):
    """Tests the NewFileObject function.

    Args:
      resolver_helper_object: the resolver helper object (instance of
                              ResolverHelper).
    """
    file_object = resolver_helper_object.NewFileObject(self._resolver_context)

    self.assertIsNotNone(file_object)

  def _TestNewFileSystem(self, resolver_helper_object):
    """Tests the NewFileSystem function.

    Args:
      resolver_helper_object: the resolver helper object (instance of
                              ResolverHelper).
    """
    file_system = resolver_helper_object.NewFileSystem(self._resolver_context)

    self.assertIsNotNone(file_system)

  def _TestNewFileSystemRaisesRuntimeError(self, resolver_helper_object):
    """Tests the NewFileSystem function raises a RuntimeError.

    Args:
      resolver_helper_object: the resolver helper object (instance of
                              ResolverHelper).
    """
    with self.assertRaises(RuntimeError):
      _ = resolver_helper_object.NewFileSystem(self._resolver_context)

  def _TestOpenFileObject(self, resolver_helper_object, path_spec):
    """Tests the OpenFileObject function.

    Args:
      resolver_helper_object: the resolver helper object (instance of
                              ResolverHelper).
      path_spec: the path specification (instance of PathSpec).
    """
    file_object = resolver_helper_object.OpenFileObject(
        path_spec, self._resolver_context)

    self.assertIsNotNone(file_object)

    file_object.close()
