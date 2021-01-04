# -*- coding: utf-8 -*-
"""Shared test cases."""

from dfvfs.lib import errors
from dfvfs.resolver import context
from dfvfs.resolver_helpers import resolver_helper

from tests import test_lib as shared_test_lib


class TestResolverHelper(resolver_helper.ResolverHelper):
  """Test resolver helper."""

  # pylint: disable=redundant-returns-doc,unused-argument

  TYPE_INDICATOR = 'TEST'

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object, which is None for testing.
    """
    return None


class ResolverHelperTestCase(shared_test_lib.BaseTestCase):
  """The unit test case for resolver helper implementations."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def _TestNewFileObject(self, resolver_helper_object, path_spec):
    """Tests the NewFileObject function.

    Args:
      resolver_helper_object (ResolverHelper): resolver helper.
      path_spec (PathSpec): path specification.
    """
    file_object = resolver_helper_object.NewFileObject(
        self._resolver_context, path_spec)

    self.assertIsNotNone(file_object)

  def _TestNewFileSystem(self, resolver_helper_object, path_spec):
    """Tests the NewFileSystem function.

    Args:
      resolver_helper_object (ResolverHelper): resolver helper.
      path_spec (PathSpec): path specification.
    """
    file_system = resolver_helper_object.NewFileSystem(
        self._resolver_context, path_spec)

    self.assertIsNotNone(file_system)

  def _TestNewFileSystemRaisesNotSupported(
      self, resolver_helper_object, path_spec):
    """Tests the NewFileSystem function raises NotSupported.

    Args:
      resolver_helper_object (ResolverHelper): resolver helper.
      path_spec (PathSpec): path specification.
    """
    with self.assertRaises(errors.NotSupported):
      resolver_helper_object.NewFileSystem(self._resolver_context, path_spec)

  def _TestOpenFileObject(self, resolver_helper_object, path_spec):
    """Tests the OpenFileObject function.

    Args:
      resolver_helper_object (ResolverHelper): resolver helper.
      path_spec (PathSpec): path specification.
    """
    file_object = resolver_helper_object.OpenFileObject(
        path_spec, self._resolver_context)

    self.assertIsNotNone(file_object)
