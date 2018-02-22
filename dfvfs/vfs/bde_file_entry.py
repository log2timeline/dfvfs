# -*- coding: utf-8 -*-
"""The BDE file entry implementation."""

from __future__ import unicode_literals

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry


class BDEFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """File system file entry that uses pybde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file

    Raises:
      BackEndError: when the BDE volume is missing.
    """
    bde_volume = file_system.GetBDEVolume()
    if bde_volume is None:
      raise errors.BackEndError('Missing BDE volume.')

    super(BDEFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._bde_volume = bde_volume
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = super(BDEFileEntry, self)._GetStat()

    stat_object.size = self._bde_volume.get_size()

    return stat_object

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    timestamp = self._bde_volume.get_creation_time_as_integer()
    return dfdatetime_filetime.Filetime(timestamp=timestamp)
