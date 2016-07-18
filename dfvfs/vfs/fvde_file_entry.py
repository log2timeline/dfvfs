# -*- coding: utf-8 -*-
"""The FVDE file entry implementation."""

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class FVDEFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Class that implements a file entry object using FVDE."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      VFSStat: stat object.

    Raises:
      BackEndError: when the FVDE file is missing.
    """
    fvde_volume = self._file_system.GetFVDEVolume()
    if fvde_volume is None:
      raise errors.BackEndError(u'Missing FVDE volume.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = fvde_volume.get_size()

    # Date and time stat information.

    # Ownership and permissions stat information.

    # File entry type stat information.
    stat_object.type = stat_object.TYPE_FILE

    # Other stat information.

    return stat_object
