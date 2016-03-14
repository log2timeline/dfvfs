# -*- coding: utf-8 -*-
"""The zip file system implementation."""

import zipfile

# This is necessary to prevent a circular import.
import dfvfs.vfs.zip_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import zip_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


class ZipFileSystem(file_system.FileSystem):
  """Class that implements a file system object using zipfile.

  Attributes:
    encoding: string containing the file entry name encoding.
  """

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def __init__(self, resolver_context, encoding=u'utf-8'):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      encoding: optional string containing file entry name encoding.
    """
    super(ZipFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._zip_file = None
    self.encoding = encoding

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._zip_file.close()
    self._zip_file = None

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
      zip_file = zipfile.ZipFile(file_object, 'r')
    except:
      file_object.close()
      raise

    self._file_object = file_object
    self._zip_file = zip_file

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    zip_info = None
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return True

    try:
      zip_info = self._zip_file.getinfo(location[1:])
    except KeyError:
      pass

    return zip_info is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.ZipFileEntry) or None.
    """
    zip_info = None
    location = getattr(path_spec, u'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return dfvfs.vfs.zip_file_entry.ZipFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    try:
      zip_info = self._zip_file.getinfo(location[1:])
    except KeyError:
      pass

    if zip_info is None:
      return
    return dfvfs.vfs.zip_file_entry.ZipFileEntry(
        self._resolver_context, self, path_spec, zip_info=zip_info)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = zip_path_spec.ZipPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetZipFile(self):
    """Retrieves the zip file object.

    Returns:
      The zip file object (instance of zipfile.ZipFile).
    """
    return self._zip_file
