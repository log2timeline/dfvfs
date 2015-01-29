# -*- coding: utf-8 -*-
"""The compressed stream file entry implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.compressed_stream_io

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class CompressedStreamFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements a compressed stream file entry object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
    """
    super(CompressedStreamFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._compressed_stream = None

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the compressed stream is missing.
    """
    if self._compressed_stream is None:
      self._compressed_stream = self.GetFileObject()

    if self._compressed_stream is None:
      raise errors.BackEndError(u'Missing compressed stream.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = self._compressed_stream.get_size()

    # Date and time stat information.

    # Ownership and permissions stat information.

    # File entry type stat information.
    stat_object.type = stat_object.TYPE_FILE

    # Other stat information.

    return stat_object

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    file_object = dfvfs.file_io.compressed_stream_io.CompressedStream(
        self._resolver_context)
    file_object.open(path_spec=self.path_spec)
    return file_object
