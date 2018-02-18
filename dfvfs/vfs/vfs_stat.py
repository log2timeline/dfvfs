# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) stat object interface."""

from __future__ import unicode_literals

# Note that if this file is name stat.py it will cause naming conflicts
# if used in combination with 'import stat'.

# Note that the stat object is currently kept around for backwards
# compatibility. Having a file (entry) attribute object might be more
# flexible in dealing with e.g. NTFS attributes.

from dfvfs.lib import definitions


class VFSStat(object):
  """Class that implements the VFS stat object interface."""

  TYPE_DEVICE = definitions.FILE_ENTRY_TYPE_DEVICE
  TYPE_DIRECTORY = definitions.FILE_ENTRY_TYPE_DIRECTORY
  TYPE_FILE = definitions.FILE_ENTRY_TYPE_FILE
  TYPE_LINK = definitions.FILE_ENTRY_TYPE_LINK
  TYPE_SOCKET = definitions.FILE_ENTRY_TYPE_SOCKET
  TYPE_PIPE = definitions.FILE_ENTRY_TYPE_PIPE

  def __init__(self):
    """Initializes the stat object."""
    super(VFSStat, self).__init__()

    # File data stat information.
    self.size = None

    # Date and time stat information.
    self.atime = None
    self.ctime = None
    self.mtime = None

    # Ownership and permissions stat information.
    self.mode = None
    self.uid = None
    self.gid = None

    # File entry type stat information.
    self.type = None

    # Other stat information.
    # self.ino = None
    # self.dev = None
    # self.nlink = None
    self.fs_type = None
    self.is_allocated = True
