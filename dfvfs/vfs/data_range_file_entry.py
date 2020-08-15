# -*- coding: utf-8 -*-
"""The data range file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class DataRangeFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """File entry that represents a data range."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

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
          entry emulated by the corresponding file system.

    Raises:
      ValueError: if a derived file entry class does not define a type
          indicator.
    """
    super(DataRangeFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetStat(self):
    """Retrieves a stat object.

    Returns:
      VFSStat: a stat object.

    Raises:
      BackEndError: when the encoded stream is missing.
    """
    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = self.path_spec.range_size

    # File entry type stat information.
    stat_object.type = stat_object.TYPE_FILE

    return stat_object
