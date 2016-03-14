# -*- coding: utf-8 -*-
"""The TAR file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import py2to3
from dfvfs.path import tar_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class TARDirectory(file_entry.Directory):
  """Class that implements a directory object using tarfile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.TARPathSpec).
    """
    location = getattr(self.path_spec, u'location', None)

    if (location is None or
        not location.startswith(self._file_system.PATH_SEPARATOR)):
      return

    tar_file = self._file_system.GetTARFile()
    for tar_info in tar_file.getmembers():
      path = tar_info.name

      # Determine if the start of the TAR info name is similar to
      # the location string. If not the file TAR info refers to is not in
      # the same directory. Note that the TAR info name does not have the
      # leading path separator as the location string does.
      if not path or not path.startswith(location[1:]):
        continue

      _, suffix = self._file_system.GetPathSegmentAndSuffix(location[1:], path)

      # Ignore anything that is part of a sub directory or the directory itself.
      if suffix or path == location:
        continue

      path_spec_location = self._file_system.JoinPath([path])
      yield tar_path_spec.TARPathSpec(
          location=path_spec_location, parent=self.path_spec.parent)


class TARFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using tarfile."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, tar_info=None):
    """Initializes the file entry object.
    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification (instance of PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system.
      tar_info: optional TAR info object (instance of tarfile.TARInfo).
    """
    super(TARFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._tar_info = tar_info

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return TARDirectory(self._file_system, self.path_spec)
    return

  def _GetLink(self):
    """Retrieves the link.

    Raises:
      BackEndError: when the TAR info is missing in a non-virtual file entry.
    """
    if self._link is None:
      tar_info = self.GetTARInfo()
      if not self._is_virtual and tar_info is None:
        raise errors.BackEndError(
            u'Missing TAR info in non-virtual file entry.')

      self._link = tar_info.linkname

    return self._link

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the TAR info is missing in a non-virtual file entry.
    """
    tar_info = self.GetTARInfo()
    if not self._is_virtual and tar_info is None:
      raise errors.BackEndError(u'Missing TAR info in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(tar_info, u'size', None)

    # Date and time stat information.
    stat_object.mtime = getattr(tar_info, u'mtime', None)

    # Ownership and permissions stat information.
    stat_object.mode = getattr(tar_info, u'mode', None)
    stat_object.uid = getattr(tar_info, u'uid', None)
    stat_object.gid = getattr(tar_info, u'gid', None)

    # TODO: implement support for:
    # stat_object.uname = getattr(tar_info, u'uname', None)
    # stat_object.gname = getattr(tar_info, u'gname', None)

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if self._is_virtual or tar_info.isdir():
      stat_object.type = stat_object.TYPE_DIRECTORY
    elif tar_info.isfile():
      stat_object.type = stat_object.TYPE_FILE
    elif tar_info.issym() or tar_info.islnk():
      stat_object.type = stat_object.TYPE_LINK
    elif tar_info.ischr() or tar_info.isblk():
      stat_object.type = stat_object.TYPE_DEVICE
    elif tar_info.isfifo():
      stat_object.type = stat_object.TYPE_PIPE

    # TODO: determine if this covers all the types:
    # REGTYPE, AREGTYPE, LNKTYPE, SYMTYPE, DIRTYPE, FIFOTYPE, CONTTYPE,
    # CHRTYPE, BLKTYPE, GNUTYPE_SPARSE

    # Other stat information.
    # tar_info.pax_headers

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    tar_info = self.GetTARInfo()

    # Note that the root file entry is virtual and has no tar_info.
    if tar_info is None:
      return u''

    path = getattr(tar_info, u'name', None)
    if path is not None and not isinstance(path, py2to3.UNICODE_TYPE):
      try:
        path = path.decode(self._file_system.encoding)
      except UnicodeDecodeError:
        path = None
    return self._file_system.BasenamePath(path)

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield TARFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      The parent file entry (instance of FileEntry) or None.
    """
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return

    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    path_spec = tar_path_spec.TARPathSpec(
        location=parent_location, parent=parent_path_spec)
    return TARFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetTARInfo(self):
    """Retrieves the TAR info object.

    Returns:
      The TAR info object (instance of tarfile.TARInfo).

    Raises:
      ValueError: if the path specification is incorrect.
    """
    if not self._tar_info:
      location = getattr(self.path_spec, u'location', None)
      if location is None:
        raise ValueError(u'Path specification missing location.')

      if not location.startswith(self._file_system.LOCATION_ROOT):
        raise ValueError(u'Invalid location in path specification.')

      if len(location) == 1:
        return

      tar_file = self._file_system.GetTARFile()
      self._tar_info = tar_file.getmember(location[1:])

    return self._tar_info
