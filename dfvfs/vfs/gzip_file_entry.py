# -*- coding: utf-8 -*-
"""The gzip file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class GzipFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements a file entry object using gzip."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the gzip file is missing.
    """
    gzip_file = self.GetFileObject()
    if not gzip_file:
      raise errors.BackEndError(
          u'Unable to open gzip file: {0:s}.'.format(self.path_spec.comparable))

    try:
      stat_object = vfs_stat.VFSStat()

      # File data stat information.
      stat_object.size = gzip_file.uncompressed_data_size

      # Date and time stat information.
      stat_object.mtime = gzip_file.modification_time

      # Ownership and permissions stat information.

      # File entry type stat information.
      stat_object.type = stat_object.TYPE_FILE

      # Other stat information.
      # gzip_file.comment
      # gzip_file.operating_system
      # gzip_file.original_filename

    finally:
      gzip_file.close()

    return stat_object
