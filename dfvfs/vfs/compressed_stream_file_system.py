# -*- coding: utf-8 -*-
"""The compressed stream file system implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import compressed_stream_path_spec
from dfvfs.vfs import compressed_stream_file_entry
from dfvfs.vfs import root_only_file_system


class CompressedStreamFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a compresses stream file system object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_COMPRESSED_STREAM

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(CompressedStreamFileSystem, self).__init__(resolver_context)
    self._compression_method = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._compression_method = None

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    compression_method = getattr(path_spec, u'compression_method', None)
    if not compression_method:
      raise errors.PathSpecError(
          u'Unsupported path specification without compression method.')

    self._compression_method = compression_method

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    return compressed_stream_file_entry.CompressedStreamFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = compressed_stream_path_spec.CompressedStreamPathSpec(
        compression_method=self._compression_method,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
