# -*- coding: utf-8 -*-
"""The BDE file entry implementation."""

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class BDEFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements a file entry object using BDE."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the BDE file is missing.
    """
    bde_volume = self._file_system.GetBDEVolume()
    if bde_volume is None:
      raise errors.BackEndError(u'Missing BDE volume.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = bde_volume.get_size()

    # Date and time stat information.
    timestamp = bde_volume.get_creation_time_as_integer()
    date_time_values = dfdatetime_filetime.Filetime(timestamp=timestamp)

    stat_time, stat_time_nano = date_time_values.CopyToStatTimeTuple()
    if stat_time is not None:
      stat_object.crtime = stat_time
      stat_object.crtime_nano = stat_time_nano

    # Ownership and permissions stat information.

    # File entry type stat information.
    stat_object.type = stat_object.TYPE_FILE

    # Other stat information.

    return stat_object
