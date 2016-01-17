# -*- coding: utf-8 -*-
"""The BDE file entry implementation."""

from dfvfs.lib import date_time
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
    date_time_values = date_time.Filetime(
        bde_volume.get_creation_time_as_integer())

    stat_time, stat_time_nano = date_time_values.CopyToStatObject()
    if stat_time is not None:
      stat_object.crtime = stat_time
      stat_object.crtime_nano = stat_time_nano

    # Ownership and permissions stat information.

    # File entry type stat information.
    stat_object.type = stat_object.TYPE_FILE

    # Other stat information.

    return stat_object
