# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) attribute interface."""

from dfvfs.lib import definitions


class Attribute(object):
  """Attribute interface."""

  @property
  def type_indicator(self):
    """str: type indicator or None if not known."""
    return getattr(self, 'TYPE_INDICATOR', None)


class StatAttribute(object):
  """Attribute that represents a POSIX stat.

  Attributes:
    group_identifier (int): group identifier (GID), equivalent to st_gid.
    inode_number (int): number of the corresponding inode, equivalent to st_ino.
    mode (int): access mode, equivalent to st_mode.
    number_of_links (int): number of hard links, equivalent to st_nlink.
    owner_identifier (int): user identifier (UID) of the owner, equivalent to
        st_uid.
    size (int): size, in number of bytes, equivalent to st_size.
    type (str): file type, value derived from st_mode >> 12.
  """

  TYPE_DEVICE = definitions.FILE_ENTRY_TYPE_DEVICE
  TYPE_DIRECTORY = definitions.FILE_ENTRY_TYPE_DIRECTORY
  TYPE_FILE = definitions.FILE_ENTRY_TYPE_FILE
  TYPE_LINK = definitions.FILE_ENTRY_TYPE_LINK
  TYPE_SOCKET = definitions.FILE_ENTRY_TYPE_SOCKET
  TYPE_PIPE = definitions.FILE_ENTRY_TYPE_PIPE
  TYPE_WHITEOUT = definitions.FILE_ENTRY_TYPE_WHITEOUT

  def __init__(self):
    """Initializes an attribute."""
    super(StatAttribute, self).__init__()
    self.group_identifier = None
    self.inode_number = None
    self.mode = None
    self.number_of_links = None
    self.owner_identifier = None
    self.size = None
    self.type = None

    # TODO: consider adding st_dev, st_rdev, st_blksize or st_blocks.
