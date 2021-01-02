# -*- coding: utf-8 -*-
"""The EXT file system implementation."""

import pyfsext

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import ext_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import ext_file_entry


class EXTFileSystem(file_system.FileSystem):
  """File system that uses pyfsext."""

  ROOT_DIRECTORY_INODE_NUMBER = 2

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EXT

  def __init__(self, resolver_context, path_spec):
    """Initializes an EXT file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(EXTFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._fsext_volume = None

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    self._fsext_volume = None
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

    fsext_volume = pyfsext.volume()
    fsext_volume.open_file_object(file_object)

    self._file_object = file_object
    self._fsext_volume = fsext_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by inode is faster than opening a file by location.
    fsext_file_entry = None
    location = getattr(path_spec, 'location', None)
    inode = getattr(path_spec, 'inode', None)

    try:
      if inode is not None:
        fsext_file_entry = self._fsext_volume.get_file_entry_by_inode(inode)
      elif location is not None:
        fsext_file_entry = self._fsext_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    return fsext_file_entry is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      EXTFileEntry: file entry or None if not available.

    Raises:
      BackEndError: if the file entry cannot be opened.
    """
    # Opening a file by inode is faster than opening a file by location.
    fsext_file_entry = None
    location = getattr(path_spec, 'location', None)
    inode = getattr(path_spec, 'inode', None)

    if (location == self.LOCATION_ROOT or
        inode == self.ROOT_DIRECTORY_INODE_NUMBER):
      fsext_file_entry = self._fsext_volume.get_root_directory()
      return ext_file_entry.EXTFileEntry(
          self._resolver_context, self, path_spec,
          fsext_file_entry=fsext_file_entry, is_root=True)

    try:
      if inode is not None:
        fsext_file_entry = self._fsext_volume.get_file_entry_by_inode(
            inode)
      elif location is not None:
        fsext_file_entry = self._fsext_volume.get_file_entry_by_path(location)

    except IOError as exception:
      raise errors.BackEndError(exception)

    if fsext_file_entry is None:
      return None

    return ext_file_entry.EXTFileEntry(
        self._resolver_context, self, path_spec,
        fsext_file_entry=fsext_file_entry)

  def GetEXTFileEntryByPathSpec(self, path_spec):
    """Retrieves the EXT file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      pyfsext.file_entry: file entry.

    Raises:
      PathSpecError: if the path specification is missing location and
          inode.
    """
    # Opening a file by inode is faster than opening a file by location.
    location = getattr(path_spec, 'location', None)
    inode = getattr(path_spec, 'inode', None)

    if inode is not None:
      fsext_file_entry = self._fsext_volume.get_file_entry_by_inode(inode)
    elif location is not None:
      fsext_file_entry = self._fsext_volume.get_file_entry_by_path(location)
    else:
      raise errors.PathSpecError(
          'Path specification missing location and inode.')

    return fsext_file_entry

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      EXTFileEntry: file entry.
    """
    path_spec = ext_path_spec.EXTPathSpec(
        location=self.LOCATION_ROOT, inode=self.ROOT_DIRECTORY_INODE_NUMBER,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)
