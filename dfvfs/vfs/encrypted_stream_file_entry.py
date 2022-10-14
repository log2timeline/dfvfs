# -*- coding: utf-8 -*-
"""The encrypted stream file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.vfs import root_only_file_entry


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
          f'Unable to open encrypted stream: {self.path_spec.comparable:s}.')

    super(EncryptedStreamFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._encrypted_stream = encrypted_stream
    self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return self._encrypted_stream.get_size()
