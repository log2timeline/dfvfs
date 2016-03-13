# -*- coding: utf-8 -*-
"""The encoded stream file system implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import encoded_stream_path_spec
from dfvfs.vfs import encoded_stream_file_entry
from dfvfs.vfs import root_only_file_system


class EncodedStreamFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a compresses stream file system object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCODED_STREAM

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(EncodedStreamFileSystem, self).__init__(resolver_context)
    self._encoding_method = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._encoding_method = None

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

    encoding_method = getattr(path_spec, u'encoding_method', None)
    if not encoding_method:
      raise errors.PathSpecError(
          u'Unsupported path specification without encoding method.')

    self._encoding_method = encoding_method

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    return encoded_stream_file_entry.EncodedStreamFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = encoded_stream_path_spec.EncodedStreamPathSpec(
        encoding_method=self._encoding_method,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
