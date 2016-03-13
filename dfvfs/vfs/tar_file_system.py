# -*- coding: utf-8 -*-
"""The TAR file system implementation."""

import tarfile

# This is necessary to prevent a circular import.
import dfvfs.vfs.tar_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tar_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


class TARFileSystem(file_system.FileSystem):
  """Class that implements a file system object using tarfile.

  Attributes:
    encoding: string containing the file entry name encoding.
  """

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def __init__(self, resolver_context, encoding=u'utf-8'):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      encoding: optional string containing file entry name encoding.
    """
    super(TARFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._tar_file = None
    self.encoding = encoding

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._tar_file.close()
    self._tar_file = None

    self._file_object.close()
    self._file_object = None

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

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    try:
      # Explicitly tell tarfile not to use compression. Compression should be
      # handled by the file-like object.
      tar_file = tarfile.open(mode='r:', fileobj=file_object)
    except:
      file_object.close()
      raise

    self._file_object = file_object
    self._tar_file = tar_file

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    tar_info = None
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return True

    try:
      tar_info = self._tar_file.getmember(location[1:])
    except KeyError:
      pass

    return tar_info is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.TARFileEntry) or None.
    """
    tar_info = None
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return dfvfs.vfs.tar_file_entry.TARFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    try:
      tar_info = self._tar_file.getmember(location[1:])
    except KeyError:
      pass

    if tar_info is None:
      return
    return dfvfs.vfs.tar_file_entry.TARFileEntry(
        self._resolver_context, self, path_spec, tar_info=tar_info)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = tar_path_spec.TARPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetTARFile(self):
    """Retrieves the TAR file object.

    Returns:
      The TAR file object (instance of tarfile.TARFile).
    """
    return self._tar_file
