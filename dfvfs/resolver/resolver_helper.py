# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) resolver helper object interface."""

import abc


class ResolverHelper(object):
  """Class that implements the resolver helper object interface."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid resolver helper missing type indicator.')
    return type_indicator

  @abc.abstractmethod
  def OpenFileObject(self, path_spec, resolver_context):
    """Opens a file-like object defined by path specification.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO) or None if the path
      specification could not be resolved.
    """

  def OpenFileSystem(self, unused_path_spec, unused_resolver_context):
    """Opens a file system object defined by path specification.

       This is the fall through implementation that raises a RuntimeError.

    Args:
      unused_path_spec: the VFS path specification (instance of path.PathSpec).
      unused_resolver_context: the resolver context (instance of
                               resolver.Context).

    Raises:
      RuntimeError: since this is the fall through implementation.
    """
    # Note: not using NotImplementedError here since pylint then will complain
    # derived classes will need to implement the method, which should not
    # be the the case.
    raise RuntimeError('Missing implemention to open file system.')
