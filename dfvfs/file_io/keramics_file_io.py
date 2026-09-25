# -*- coding: utf-8 -*-
"""The Keramics file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class KeramicsFile(file_io.FileIO):
    """File input/output (IO) object using pykeramics.VfsDataStream."""

    def __init__(self, resolver_context, path_spec):
        """Initializes a file input/output (IO) object.

        Args:
          resolver_context (Context): resolver context.
          path_spec (PathSpec): a path specification.
        """
        super().__init__(resolver_context, path_spec)
        self._file_system = None
        self._keramics_data_stream = None

    def _Close(self):
        """Closes the file-like object."""
        self._keramics_data_stream = None
        self._file_system = None

    def _Open(self):
        """Opens the file-like object defined by path specification.

        Raises:
          IOError: if the file-like object could not be opened.
          OSError: if the file-like object could not be opened.
        """
        self._file_system = resolver.Resolver.OpenFileSystem(
            self._path_spec, resolver_context=self._resolver_context
        )
        file_entry = self._file_system.GetFileEntryByPathSpec(self._path_spec)
        if not file_entry:
            raise IOError("Unable to open file entry.")

        data_stream = getattr(self._path_spec, "data_stream", None)
        pykeramics_data_stream = file_entry.GetKeramicsDataStream(name=data_stream)
        if not pykeramics_data_stream:
            raise IOError("Unable to retrieve Keramics data stream.")

        self._keramics_data_stream = pykeramics_data_stream

    # Note: that the following functions do not follow the style guide
    # because they are part of the file-like object interface.
    # pylint: disable=invalid-name

    def read(self, size=None):
        """Reads a byte string from the file-like object at the current offset.

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
        if not self._is_open:
            raise IOError("Not opened.")

        if size is None:
            size = self._keramics_data_stream.get_size()

        try:
            return self._keramics_data_stream.read(size)
        except (RuntimeError, ValueError) as exception:
            raise IOError(exception)

    def seek(self, offset, whence=os.SEEK_SET):
        """Seeks to an offset within the file-like object.

        Args:
          offset (int): offset to seek to.
          whence (Optional(int)): value that indicates whether offset is an absolute
              or relative position within the file.

        Raises:
          IOError: if the seek failed.
          OSError: if the seek failed.
        """
        if not self._is_open:
            raise IOError("Not opened.")

        try:
            self._keramics_data_stream.seek(offset, whence)
        except (RuntimeError, ValueError) as exception:
            raise IOError(exception)

    def get_offset(self):
        """Retrieves the current offset into the file-like object.

        Return:
          int: current offset into the file-like object.

        Raises:
          IOError: if the file-like object has not been opened.
          OSError: if the file-like object has not been opened.
        """
        if not self._is_open:
            raise IOError("Not opened.")

        try:
            return self._keramics_data_stream.get_offset()
        except RuntimeError as exception:
            raise IOError(exception)

    def get_size(self):
        """Retrieves the size of the file-like object.

        Returns:
          int: size of the file-like object data.

        Raises:
          IOError: if the file-like object has not been opened.
          OSError: if the file-like object has not been opened.
        """
        if not self._is_open:
            raise IOError("Not opened.")

        try:
            return self._keramics_data_stream.get_size()
        except RuntimeError as exception:
            raise IOError(exception)
