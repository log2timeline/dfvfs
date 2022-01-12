# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) extent."""


class Extent(object):
  """Extent.

  Attributes:
    extent_type (str): type of the extent, for example EXTENT_TYPE_SPARSE.
    offset (int): offset of the extent relative from the start of the file
        system in bytes.
    size (int): size of the extent in bytes.
  """

  def __init__(self, extent_type=None, offset=None, size=None):
    """Initializes an extent.

    Args:
      extent_type (Optional[str]): type of the extent, for example
          EXTENT_TYPE_SPARSE.
      offset (Optional[int]): offset of the extent relative from the start of
          the file system in bytes.
      size (Optional{int]): size of the extent in bytes.
    """
    super(Extent, self).__init__()
    self.extent_type = extent_type
    self.offset = offset
    self.size = size
