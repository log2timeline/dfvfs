# -*- coding: utf-8 -*-
"""The Keramics attribute implementation."""

import os

from dfvfs.lib import errors
from dfvfs.vfs import attribute


class KeramicsExtendedAttribute(attribute.Attribute):
    """Keramics extended attribute that uses pykeramics."""

    def __init__(self, pykeramics_extended_attribute):
        """Initializes an attribute.

        Args:
          pykeramics_extended_attribute (pykeramics.extended_attribute): pykeramics
              extended attribute.

        Raises:
          BackEndError: if the pykeramics extended attribute is missing.
        """
        if not pykeramics_extended_attribute:
            raise errors.BackEndError("Missing pykeramics extended attribute.")

        super().__init__()
        self._keramics_data_stream = pykeramics_extended_attribute.get_data_stream()
        self._keramics_extended_attribute = pykeramics_extended_attribute

    @property
    def name(self):
        """str: name."""
        return self._keramics_extended_attribute.name.to_string()

    def GetExtents(self):
        """Retrieves the extents.

        Returns:
          list[Extent]: the extents of the attribute data.
        """
        extents = []

        # TODO: add support for extents
        return extents

    # Note: that the following functions do not follow the style guide
    # because they are part of the file-like object interface.
    # pylint: disable=invalid-name

    def read(self, size=None):
        """Reads a byte string from the file input/output (IO) object.

        The function will read a byte string of the specified size or
        all of the remaining data if no size was specified.

        Args:
          size (Optional[int]): number of bytes to read, where None is all
              remaining data.

        Returns:
          bytes: data read.

        Raises:
          IOError: if the read failed.
          OSError: if the read failed.
        """
        if size is None:
            size = self._keramics_data_stream.get_size()

        try:
            return self._keramics_data_stream.read(size)
        except (RuntimeError, ValueError) as exception:
            raise IOError(exception)

    def seek(self, offset, whence=os.SEEK_SET):
        """Seeks to an offset within the file input/output (IO) object.

        Args:
          offset (int): offset to seek.
          whence (Optional[int]): value that indicates whether offset is an
              absolute or relative position within the file.

        Raises:
          IOError: if the seek failed.
          OSError: if the seek failed.
        """
        self._keramics_extended_attribute.seek_offset(offset, whence)

    # get_offset() is preferred above tell() by the libbfio layer used in libyal.
    def get_offset(self):
        """Retrieves the current offset into the file input/output (IO) object.

        Returns:
          int: current offset into the file input/output (IO) object.
        """
        return self._keramics_extended_attribute.get_offset()

    # Pythonesque alias for get_offset().
    def tell(self):
        """Retrieves the current offset into the file input/output (IO) object."""
        return self.get_offset()

    def get_size(self):
        """Retrieves the size of the file input/output (IO) object.

        Returns:
          int: size of the file input/output (IO) object.
        """
        return self._keramics_extended_attribute.get_size()

    def seekable(self):
        """Determines if a file input/output (IO) object is seekable.

        Returns:
          bool: True since a file IO object provides a seek method.
        """
        return True
