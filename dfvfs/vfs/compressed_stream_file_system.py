# -*- coding: utf-8 -*-
"""The compressed stream file system implementation."""

from dfvfs.lib import definitions
from dfvfs.path import compressed_stream_path_spec
from dfvfs.vfs import compressed_stream_file_entry
from dfvfs.vfs import root_only_file_system


class CompressedStreamFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a compresses stream file system object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def __init__(self, resolver_context, compression_method, path_spec):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      compression_method: optional method used to the compress the data.
                          The default is None.
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(CompressedStreamFileSystem, self).__init__(resolver_context)
    self._compression_method = compression_method
    self._path_spec = path_spec

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = compressed_stream_path_spec.CompressedStreamPathSpec(
        compression_method=self._compression_method, parent=self._path_spec)
    return compressed_stream_file_entry.CompressedStreamFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)
