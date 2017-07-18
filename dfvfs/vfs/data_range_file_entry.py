# -*- coding: utf-8 -*-
"""The data range file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class DataRangeFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements a data range file entry object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the encoded stream is missing.
    """
    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = self.path_spec.range_size

    # File entry type stat information.
    stat_object.type = stat_object.TYPE_FILE

    return stat_object
