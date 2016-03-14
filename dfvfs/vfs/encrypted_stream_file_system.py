# -*- coding: utf-8 -*-
"""The encrypted stream file system implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import encrypted_stream_path_spec
from dfvfs.vfs import encrypted_stream_file_entry
from dfvfs.vfs import root_only_file_system


class EncryptedStreamFileSystem(root_only_file_system.RootOnlyFileSystem):
  """Class that implements a compresses stream file system object."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENCRYPTED_STREAM

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(EncryptedStreamFileSystem, self).__init__(resolver_context)
    self._encryption_method = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._encryption_method = None

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

    encryption_method = getattr(path_spec, u'encryption_method', None)
    if not encryption_method:
      raise errors.PathSpecError(
          u'Unsupported path specification without encryption method.')

    self._encryption_method = encryption_method

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    return encrypted_stream_file_entry.EncryptedStreamFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    path_spec = encrypted_stream_path_spec.EncryptedStreamPathSpec(
        encryption_method=self._encryption_method,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
