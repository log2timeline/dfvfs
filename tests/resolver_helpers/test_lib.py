# -*- coding: utf-8 -*-
"""Shared test cases."""

from __future__ import unicode_literals

from dfvfs.resolver import context
from dfvfs.resolver_helpers import resolver_helper

from tests import test_lib as shared_test_lib


class TestResolverHelper(resolver_helper.ResolverHelper):
  """Test resolver helper."""

  TYPE_INDICATOR = 'TEST'

  def __init__(self, **kwargs):
    """Initializes the resolver helper object."""
    super(TestResolverHelper, self).__init__(parent=None, **kwargs)

  def NewFileObject(self, unused_resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return


class ResolverHelperTestCase(shared_test_lib.BaseTestCase):
  """The unit test case for resolver helper implementions."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def _TestNewFileObject(self, resolver_helper_object):
    """Tests the NewFileObject function.

    Args:
      resolver_context (Context): resolver context.
    """
    file_object = resolver_helper_object.NewFileObject(self._resolver_context)

    self.assertIsNotNone(file_object)

  def _TestNewFileSystem(self, resolver_helper_object):
    """Tests the NewFileSystem function.

    Args:
      resolver_context (Context): resolver context.
    """
    file_system = resolver_helper_object.NewFileSystem(self._resolver_context)

    self.assertIsNotNone(file_system)

  def _TestNewFileSystemRaisesRuntimeError(self, resolver_helper_object):
    """Tests the NewFileSystem function raises a RuntimeError.

    Args:
      resolver_context (Context): resolver context.
    """
    with self.assertRaises(RuntimeError):
      resolver_helper_object.NewFileSystem(self._resolver_context)

  def _TestOpenFileObject(self, resolver_helper_object, path_spec):
    """Tests the OpenFileObject function.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): path specification.
    """
    file_object = resolver_helper_object.OpenFileObject(
        path_spec, self._resolver_context)

    self.assertIsNotNone(file_object)

    file_object.close()
