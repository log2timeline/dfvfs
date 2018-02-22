# -*- coding: utf-8 -*-
"""The encrypted stream file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.vfs import root_only_file_entry
from dfvfs.vfs import vfs_stat


class EncryptedStreamFileEntry(root_only_file_entry.RootOnlyFileEntry):
  """Encrypted stream file entry."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM

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

    Raises:
      BackEndError: when the encrypted stream is missing.
    """
    encrypted_stream = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=resolver_context)
    if not encrypted_stream:
      raise errors.BackEndError(
          'Unable to open encrypted stream: {0:s}.'.format(
              self.path_spec.comparable))

    super(EncryptedStreamFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._encrypted_stream = encrypted_stream
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def __del__(self):
    """Cleans up the file entry."""
    # __del__ can be invoked before __init__ has completed.
    if hasattr(self, '_encrypted_stream'):
      self._encrypted_stream.close()
      self._encrypted_stream = None

    super(EncryptedStreamFileEntry, self).__del__()

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = vfs_stat.VFSStat()

    if self._encrypted_stream:
      stat_object.size = self._encrypted_stream.get_size()

    stat_object.type = self.entry_type

    return stat_object
