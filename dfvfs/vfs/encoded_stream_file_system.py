# -*- coding: utf-8 -*-
"""The encoded stream file system implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import encoded_stream_path_spec
from dfvfs.vfs import encoded_stream_file_entry
from dfvfs.vfs import root_only_file_system


class EncodedStreamFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Encoded stream file system."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCODED_STREAM

  def __init__(self, resolver_context, path_spec):
    """Initializes an encoded file system.

    Args:
      resolver_context (Context): a resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(EncodedStreamFileSystem, self).__init__(resolver_context, path_spec)
    self._encoding_method = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._encoding_method = None

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

    encoding_method = getattr(self._path_spec, 'encoding_method', None)
    if not encoding_method:
      raise errors.PathSpecError(
          'Unsupported path specification without encoding method.')

    self._encoding_method = encoding_method

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      EncodedStreamFileEntry: a file entry or None if not available.
    """
    return encoded_stream_file_entry.EncodedStreamFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      EncodedStreamFileEntry: a file entry or None if not available.
    """
    path_spec = encoded_stream_path_spec.EncodedStreamPathSpec(
        encoding_method=self._encoding_method,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
