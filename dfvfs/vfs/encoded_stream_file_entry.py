# -*- coding: utf-8 -*-
"""The encoded stream file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.vfs import root_only_file_entry


class EncodedStreamFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements an encoded stream file entry object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCODED_STREAM

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file

    Raises:
      BackEndError: when the encoded stream is missing.
    """
    encoded_stream = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=resolver_context)
    if not encoded_stream:
      raise errors.BackEndError(
          'Unable to open encoded stream: {0:s}.'.format(
              self.path_spec.comparable))

    super(EncodedStreamFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._encoded_stream = encoded_stream
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def __del__(self):
    """Cleans up the file entry."""
    # __del__ can be invoked before __init__ has completed.
    if hasattr(self, '_encoded_stream'):
      self._encoded_stream.close()
      self._encoded_stream = None

    super(EncodedStreamFileEntry, self).__del__()

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._encoded_stream.get_size()
