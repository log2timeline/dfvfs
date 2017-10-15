# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) resolver helper object interface."""

from __future__ import unicode_literals


class ResolverHelper(object):
  """Resolver helper object interface."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          'Invalid resolver helper missing type indicator.')
    return type_indicator

  def NewFileObject(self, unused_resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.

    Raises:
      RuntimeError: if there is no implementation to create a file-like object.
    """
    # Note: not using NotImplementedError or @abc.abstractmethod here since
    # pylint then will complain derived classes will need to implement
    # abstract methods, which should not be the the case.
    raise RuntimeError('Missing implemention to create file object.')

  def NewFileSystem(self, unused_resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.

    Raises:
      RuntimeError: if there is no implementation to create a file system
          object.
    """
    # Note: not using NotImplementedError or @abc.abstractmethod here since
    # pylint then will complain derived classes will need to implement
    # abstract methods, which should not be the the case.
    raise RuntimeError('Missing implemention to create file system.')
