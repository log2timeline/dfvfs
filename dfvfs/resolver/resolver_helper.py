# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) resolver helper object interface."""

import abc


class ResolverHelper(object):
  """Class that implements the resolver helper object interface."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, u'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid resolver helper missing type indicator.')
    return type_indicator

  @abc.abstractmethod
  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """

  def NewFileSystem(self, unused_resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.FileSystem).
    """
    # Note: not using NotImplementedError or @abc.abstractmethod here since
    # pylint then will complain derived classes will need to implement
    # abstract methods, which should not be the the case.
    raise RuntimeError(u'Missing implemention to create file system.')
