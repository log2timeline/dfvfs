# -*- coding: utf-8 -*-
"""The tar file entry implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.tar_file_io

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tar_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class TarDirectory(file_entry.Directory):
  """Class that implements a directory object using tarfile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.TarPathSpec).
    """
    location = getattr(self.path_spec, 'location', None)

    if (location is None or
        not location.startswith(self._file_system.PATH_SEPARATOR)):
      return

    tar_file = self._file_system.GetTarFile()
    for tar_info in tar_file.getmembers():
      path = tar_info.name

      # Determine if the start of the tar info name is similar to
      # the location string. If not the file tar info refers to is not in
      # the same directory. Note that the tar info name does not have the
      # leading path separator as the location string does.
      if (not path or not path.startswith(location[1:])):
        continue

      _, suffix = self._file_system.GetPathSegmentAndSuffix(location[1:], path)

      # Ignore anything that is part of a sub directory or the directory itself.
      if suffix or path == location:
        continue

      path_spec_location = self._file_system.JoinPath([path])
      yield tar_path_spec.TarPathSpec(
          location=path_spec_location, parent=self.path_spec.parent)


class TarFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using tarfile."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, tar_info=None):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
      tar_info: optional tar info object (instance of tarfile.TarInfo).
                The default is None.
    """
    super(TarFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._tar_info = tar_info
    self._name = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of TarDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return TarDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the tar info is missing in a non-virtual file entry.
    """
    if self._tar_info is None:
      self._tar_info = self.GetTarInfo()

    if not self._is_virtual and self._tar_info is None:
      raise errors.BackEndError(u'Missing tar info in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(self._tar_info, 'size', None)

    # Date and time stat information.
    stat_object.mtime = getattr(self._tar_info, 'mtime', None)

    # Ownership and permissions stat information.
    stat_object.mode = getattr(self._tar_info, 'mode', None)
    stat_object.uid = getattr(self._tar_info, 'uid', None)
    stat_object.gid = getattr(self._tar_info, 'gid', None)

    # TODO: implement support for:
    # stat_object.uname = getattr(self._tar_info, 'uname', None)
    # stat_object.gname = getattr(self._tar_info, 'gname', None)

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if self._is_virtual or self._tar_info.isdir():
      stat_object.type = stat_object.TYPE_DIRECTORY
    elif self._tar_info.isfile():
      stat_object.type = stat_object.TYPE_FILE
    elif self._tar_info.issym() or self._tar_info.islnk():
      stat_object.type = stat_object.TYPE_LINK
    elif self._tar_info.ischr() or self._tar_info.isblk():
      stat_object.type = stat_object.TYPE_DEVICE
    elif self._tar_info.isfifo():
      stat_object.type = stat_object.TYPE_PIPE

    # TODO: determine if this covers all the types:
    # REGTYPE, AREGTYPE, LNKTYPE, SYMTYPE, DIRTYPE, FIFOTYPE, CONTTYPE,
    # CHRTYPE, BLKTYPE, GNUTYPE_SPARSE

    # Other stat information.
    # tar_info.linkname
    # tar_info.pax_headers

    return stat_object

  @property
  def name(self):
    """"The name of the file entry, which does not include the full path."""
    if self._name is None:
      if self._tar_info is None:
        self._tar_info = self.GetTarInfo()

      # Note that the root file entry is virtual and has no tar_info.
      if self._tar_info is None:
        self._name = u''
      else:
        path = getattr(self._tar_info, 'name', None)
        if path is not None:
          try:
            path = path.decode(self._file_system.encoding)
          except UnicodeDecodeError:
            path = None
        self._name = self._file_system.BasenamePath(path)
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield TarFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    if self._tar_info is None:
      self._tar_info = self.GetTarInfo()

    tar_file_object = self.GetTarExFileObject()
    file_object = dfvfs.file_io.tar_file_io.TarFile(
        self._resolver_context, tar_info=self._tar_info,
        tar_file_object=tar_file_object)
    file_object.open()
    return file_object

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = tar_path_spec.TarPathSpec(
        location=parent_location, parent=parent_path_spec)
    return TarFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetTarExFileObject(self):
    """Retrieves the tar extracted file-like object.

    Returns:
      The extracted file-like object (instance of tarfile.ExFileObject).
    """
    if self._tar_info is None:
      self._tar_info = self.GetTarInfo()

    tar_file = self._file_system.GetTarFile()
    return tar_file.extractfile(self._tar_info)

  def GetTarInfo(self):
    """Retrieves the tar info object.

    Returns:
      The tar info object (instance of tarfile.TarInfo).

    Raises:
      ValueError: if the path specification is incorrect.
    """
    location = getattr(self.path_spec, 'location', None)

    if location is None:
      raise ValueError(u'Path specification missing location.')

    if not location.startswith(self._file_system.LOCATION_ROOT):
      raise ValueError(u'Invalid location in path specification.')

    if len(location) == 1:
      return

    tar_file = self._file_system.GetTarFile()
    return tar_file.getmember(location[1:])
