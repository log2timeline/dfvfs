# -*- coding: utf-8 -*-
"""The compressed stream file system implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import compressed_stream_path_spec
from dfvfs.vfs import compressed_stream_file_entry
from dfvfs.vfs import root_only_file_system


class CompressedStreamFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Compressed stream file system."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def __init__(self, resolver_context, path_spec):
    """Initializes a compressed stream file system.

    Args:
      resolver_context (Context): a resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(CompressedStreamFileSystem, self).__init__(
        resolver_context, path_spec)
    self._compression_method = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._compression_method = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    compression_method = getattr(self._path_spec, 'compression_method', None)
    if not compression_method:
      raise errors.PathSpecError(
          'Unsupported path specification without compression method.')

    self._compression_method = compression_method

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      CompressedStreamFileEntry: a file entry or None if not available.
    """
    return compressed_stream_file_entry.CompressedStreamFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      CompressedStreamFileEntry: a file entry or None if not available.
    """
    path_spec = compressed_stream_path_spec.CompressedStreamPathSpec(
        compression_method=self._compression_method,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
