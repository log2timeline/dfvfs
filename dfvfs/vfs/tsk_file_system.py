# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file system implementation."""

import pytsk3

# This is necessary to prevent a circular import.
import dfvfs.vfs.tsk_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import tsk_image
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


class TSKFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pytsk3."""

  LOCATION_ROOT = u'/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def __init__(self, resolver_context):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(TSKFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._tsk_file_system = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._tsk_file_system = None

    self._file_object.close()
    self._file_object = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
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

    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)
    tsk_file_system = pytsk3.FS_Info(tsk_image_object)

    self._file_object = file_object
    self._tsk_file_system = tsk_file_system

  def _GetRootInode(self):
    """Retrieves the root inode or None."""
    # Note that because pytsk3.FS_Info does not explicitly define info
    # we need to check if the attribute exists and has a value other
    # than None
    if getattr(self._tsk_file_system, u'info', None) is None:
      return

    # Note that because pytsk3.TSK_FS_INFO does not explicitly define
    # root_inum we need to check if the attribute exists and has a value
    # other than None
    return getattr(self._tsk_file_system.info, u'root_inum', None)

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    tsk_file = None
    inode = getattr(path_spec, u'inode', None)
    location = getattr(path_spec, u'location', None)

    try:
      if inode is not None:
        tsk_file = self._tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        tsk_file = self._tsk_file_system.open(location)

    except IOError:
      pass

    return tsk_file is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    # Opening a file by inode number is faster than opening a file by location.
    tsk_file = None
    inode = getattr(path_spec, u'inode', None)
    location = getattr(path_spec, u'location', None)

    root_inode = self._GetRootInode()
    if inode is not None and root_inode is not None and inode == root_inode:
      tsk_file = self._tsk_file_system.open(self.LOCATION_ROOT)
      return dfvfs.vfs.tsk_file_entry.TSKFileEntry(
          self._resolver_context, self, path_spec, tsk_file=tsk_file,
          is_root=True)

    elif location is not None and location == self.LOCATION_ROOT:
      tsk_file = self._tsk_file_system.open(self.LOCATION_ROOT)
      return dfvfs.vfs.tsk_file_entry.TSKFileEntry(
          self._resolver_context, self, path_spec, tsk_file=tsk_file,
          is_root=True)

    try:
      if inode is not None:
        tsk_file = self._tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        tsk_file = self._tsk_file_system.open(location)

    except IOError:
      pass

    if tsk_file is None:
      return

    # TODO: is there a way to determine the parent inode number here?
    return dfvfs.vfs.tsk_file_entry.TSKFileEntry(
        self._resolver_context, self, path_spec, tsk_file=tsk_file)

  def GetFsInfo(self):
    """Retrieves the file system info object.

    Returns:
      The SleuthKit file system info object (instance of
      pytsk3.FS_Info).
    """
    return self._tsk_file_system

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    kwargs = {}

    root_inode = self._GetRootInode()
    if root_inode is not None:
      kwargs[u'inode'] = root_inode

    kwargs[u'location'] = self.LOCATION_ROOT
    kwargs[u'parent'] = self._path_spec.parent

    path_spec = tsk_path_spec.TSKPathSpec(**kwargs)
    return self.GetFileEntryByPathSpec(path_spec)
