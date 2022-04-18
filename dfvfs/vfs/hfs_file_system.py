# -*- coding: utf-8 -*-
"""The HFS file system implementation."""

import pyfshfs

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import hfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import hfs_file_entry


class HFSFileSystem(file_system.FileSystem):
  """File system that uses pyfshfs."""

  ROOT_DIRECTORY_IDENTIFIER_NUMBER = 2

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_HFS

  def __init__(self, resolver_context, path_spec):
    """Initializes an HFS file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(HFSFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._fshfs_volume = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fshfs_volume = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    fshfs_volume = pyfshfs.volume()
    fshfs_volume.open_file_object(file_object)

    self._file_object = file_object
    self._fshfs_volume = fshfs_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by identifier is faster than opening a file by location.
    fshfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    try:
      if identifier is not None:
        fshfs_file_entry = self._fshfs_volume.get_file_entry_by_identifier(
            identifier)
      elif location is not None:
        fshfs_file_entry = self._fshfs_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    return fshfs_file_entry is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      HFSFileEntry: file entry or None if not available.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by identifier is faster than opening a file by location.
    fshfs_file_entry = None
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    if (location == self.LOCATION_ROOT or
        identifier == self.ROOT_DIRECTORY_IDENTIFIER_NUMBER):
      fshfs_file_entry = self._fshfs_volume.get_root_directory()
      return hfs_file_entry.HFSFileEntry(
          self._resolver_context, self, path_spec,
          fshfs_file_entry=fshfs_file_entry, is_root=True)

    try:
      if identifier is not None:
        fshfs_file_entry = self._fshfs_volume.get_file_entry_by_identifier(
            identifier)
      elif location is not None:
        fshfs_file_entry = self._fshfs_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    if fshfs_file_entry is None:
      return None

    return hfs_file_entry.HFSFileEntry(
        self._resolver_context, self, path_spec,
        fshfs_file_entry=fshfs_file_entry)

  def GetHFSFileEntryByPathSpec(self, path_spec):
    """Retrieves the HFS file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      pyfshfs.file_entry: file entry.

    Raises:
      PathSpecError: if the path specification is missing location and
          identifier.
    """
    # Opening a file by identifier is faster than opening a file by location.
    location = getattr(path_spec, 'location', None)
    identifier = getattr(path_spec, 'identifier', None)

    if identifier is not None:
      fshfs_file_entry = self._fshfs_volume.get_file_entry_by_identifier(
          identifier)
    elif location is not None:
      fshfs_file_entry = self._fshfs_volume.get_file_entry_by_path(location)
    else:
      raise errors.PathSpecError(
          'Path specification missing location and identifier.')

    return fshfs_file_entry

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      HFSFileEntry: file entry.
    """
    path_spec = hfs_path_spec.HFSPathSpec(
        location=self.LOCATION_ROOT,
        identifier=self.ROOT_DIRECTORY_IDENTIFIER_NUMBER,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
