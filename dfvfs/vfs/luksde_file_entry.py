# -*- coding: utf-8 -*-
"""The LUKSDE file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import root_only_file_entry


class LUKSDEFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """File system file entry that uses pyluksde."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LUKSDE

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
      BackEndError: when the LUKSDE volume is missing.
    """
    luksde_volume = file_system.GetLUKSDEVolume()
    if luksde_volume is None:
      raise errors.BackEndError('Missing LUKSDE volume.')

    super(LUKSDEFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._luksde_volume = luksde_volume
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._luksde_volume.get_size()
