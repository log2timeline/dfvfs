# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) attribute interface."""

from dfvfs.lib import definitions


class Attribute(object):
  """Attribute interface."""

  @property
  def type_indicator(self):
    """str: type indicator or None if not known."""
    return getattr(self, 'TYPE_INDICATOR', None)

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents of the attribute data.
    """
    return []


class StatAttribute(object):
  """Attribute that represents a POSIX stat.

  Attributes:
    device_number (Tuple[int, int]): major and minor device number (if block or
        character device file), derived from st_rdev.
    group_identifier (int): group identifier (GID), equivalent to st_gid.
    inode_number (int): number of the corresponding inode, equivalent to st_ino.
    mode (int): access mode, equivalent to st_mode.
    number_of_links (int): number of hard links, equivalent to st_nlink.
    owner_identifier (int): user identifier (UID) of the owner, equivalent to
        st_uid.
    size (int): size, in number of bytes, equivalent to st_size.
    type (str): file type, value derived from st_mode >> 12.
  """

  TYPE_BLOCK_DEVICE = definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE
  TYPE_CHARACTER_DEVICE = definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE
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
    self.device_number = None
    self.group_identifier = None
    self.inode_number = None
    self.mode = None
    self.number_of_links = None
    self.owner_identifier = None
    self.size = None
    self.type = None

    # TODO: consider adding st_dev, st_blksize or st_blocks.
