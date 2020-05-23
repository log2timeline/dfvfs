# -*- coding: utf-8 -*-
"""The ZIP file system implementation."""

from __future__ import unicode_literals

import zipfile

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import zip_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import zip_file_entry


class ZipFileSystem(file_system.FileSystem):
  """File system that uses zipfile.

  Attributes:
    encoding (str): encoding of the file entry name.
  """

  LOCATION_ROOT = '/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def __init__(self, resolver_context, encoding='utf-8'):
    """Initializes a file system.

    Args:
      resolver_context (Context): a resolver context.
      encoding (Optional[str]): encoding of the file entry name.
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
      path_spec (PathSpec): path specification of the file system.
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

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
      path_spec (PathSpec): path specification of the file entry.

    Returns:
      bool: True if the file entry exists.
    """
    location = getattr(path_spec, 'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return False

    if len(location) == 1:
      return True

    try:
      self._zip_file.getinfo(location[1:])
      return True
    except KeyError:
      pass

    # Check if location could be a virtual directory.
    for name in self._zip_file.namelist():
      # The ZIP info name does not have the leading path separator as
      # the location string does.
      if name.startswith(location[1:]):
        return True

    return False

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification of the file entry.

    Returns:
      ZipFileEntry: a file entry or None.
    """
    if not self.FileEntryExistsByPathSpec(path_spec):
      return None

    location = getattr(path_spec, 'location', None)

    if len(location) == 1:
      return zip_file_entry.ZipFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    kwargs = {}
    try:
      kwargs['zip_info'] = self._zip_file.getinfo(location[1:])
    except KeyError:
      kwargs['is_virtual'] = True

    return zip_file_entry.ZipFileEntry(
        self._resolver_context, self, path_spec, **kwargs)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      ZipFileEntry: a file entry or None.
    """
    path_spec = zip_path_spec.ZipPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetZipFile(self):
    """Retrieves the ZIP file object.

    Returns:
      zipfile.ZipFile: a ZIP file object or None.
    """
    return self._zip_file

  def GetZipInfoByPathSpec(self, path_spec):
    """Retrieves the ZIP info for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      zipfile.ZipInfo: a ZIP info object or None if not available.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    location = getattr(path_spec, 'location', None)
    if location is None:
      raise errors.PathSpecError('Path specification missing location.')

    if not location.startswith(self.LOCATION_ROOT):
      raise errors.PathSpecError('Invalid location in path specification.')

    if len(location) > 1:
      return self._zip_file.getinfo(location[1:])

    return None
