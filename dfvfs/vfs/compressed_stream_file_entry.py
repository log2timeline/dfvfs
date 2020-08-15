# -*- coding: utf-8 -*-
"""The compressed stream file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.vfs import root_only_file_entry


class CompressedStreamFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Compressed stream file entry."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

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
      BackEndError: when the compressed stream is missing.
    """
    compressed_stream = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=resolver_context)
    if not compressed_stream:
      raise errors.BackEndError(
          'Unable to open compressed stream: {0:s}.'.format(
              self.path_spec.comparable))

    super(CompressedStreamFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._compressed_stream = compressed_stream
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def __del__(self):
    """Cleans up the file entry."""
    # __del__ can be invoked before __init__ has completed.
    if hasattr(self, '_compressed_stream'):
      self._compressed_stream.close()
      self._compressed_stream = None

    super(CompressedStreamFileEntry, self).__del__()

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._compressed_stream.get_size()
