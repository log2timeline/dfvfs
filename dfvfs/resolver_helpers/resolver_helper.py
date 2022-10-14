# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) resolver helper interface."""

from dfvfs.lib import errors


class ResolverHelper(object):
  """Resolver helper interface."""

  # pylint: disable=redundant-returns-doc,unused-argument

  def __init__(self):
    """Initializes a resolver helper.

    Raises:
      ValueError: if a derived resolver helper class does not define a type
          indicator.
    """
    super(ResolverHelper, self).__init__()

    if not getattr(self, 'TYPE_INDICATOR', None):
      raise ValueError('Missing type indicator.')

  @property
  def type_indicator(self):
    """str: type indicator."""
    # pylint: disable=no-member
    return self.TYPE_INDICATOR

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.

    Raises:
      NotSupported: if there is no implementation to create a file
          input/output (IO) object.
    """
    raise errors.NotSupported(
        'Missing implementation to create file input/output (IO) object.')

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.

    Raises:
      NotSupported: if there is no implementation to create a file system.
    """
    # pylint: disable=no-member
    raise errors.NotSupported((
        f'Missing implementation to create file system: '
        f'{self.TYPE_INDICATOR:s}.'))
