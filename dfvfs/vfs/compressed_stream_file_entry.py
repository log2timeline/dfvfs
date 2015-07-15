# -*- coding: utf-8 -*-
"""The compressed stream file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class CompressedStreamFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements a compressed stream file entry object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the compressed stream is missing.
    """
    compressed_stream = self.GetFileObject()
    if not compressed_stream:
      raise errors.BackEndError(
          u'Unable to open compressed stream: {0:s}.'.format(
              self.path_spec.comparable))

    try:
      stat_object = vfs_stat.VFSStat()

      # File data stat information.
      stat_object.size = compressed_stream.get_size()

      # Date and time stat information.

      # Ownership and permissions stat information.

      # File entry type stat information.
      stat_object.type = stat_object.TYPE_FILE

      # Other stat information.

    finally:
      compressed_stream.close()

    return stat_object
