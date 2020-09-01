# -*- coding: utf-8 -*-
"""The FVDE file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry


class FVDEFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """File system file entry that uses pyfvde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

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
      BackEndError: when the FVDE volume is missing.
    """
    fvde_volume = file_system.GetFVDEVolume()
    if fvde_volume is None:
      raise errors.BackEndError('Missing FVDE volume.')

    super(FVDEFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._fvde_volume = fvde_volume
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._fvde_volume.get_size()
