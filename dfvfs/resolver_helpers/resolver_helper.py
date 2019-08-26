# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) resolver helper interface."""

from __future__ import unicode_literals

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

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.

    Raises:
      NotSupported: if there is no implementation to create a file-like object.
    """
    raise errors.NotSupported(
        'Missing implementation to create file-like object.')

  def NewFileSystem(self, resolver_context):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.

    Raises:
      NotSupported: if there is no implementation to create a file system.
    """
    raise errors.NotSupported('Missing implementation to create file system.')
