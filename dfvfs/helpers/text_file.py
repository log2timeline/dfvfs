# -*- coding: utf-8 -*-
"""A text file interface for file-like objects."""

from __future__ import unicode_literals

import os

# Since this class implements the readlines file-like object interface
# the names of the interface functions are in lower case as an exception
# to the normal naming convention.


class TextFile(object):
  """Text file interface for file-like objects."""

  # The maximum allowed size of the read buffer.
  _MAXIMUM_READ_BUFFER_SIZE = 16 * 1024 * 1024

  def __init__(
      self, file_object, encoding='utf-8', encoding_errors='strict',
      end_of_line='\n'):
    """Initializes the text file.

    Args:
      file_object (FileIO): a file-like object to read from.
      encoding (Optional[str]): text encoding.
      encoding_errors (Optional[str]): text encoding errors handler.
      end_of_line (Optional[str]): end of line indicator.
    """
    super(TextFile, self).__init__()
    self._file_object = file_object
    self._file_object_size = file_object.get_size()
    self._encoding = encoding
    self._encoding_errors = encoding_errors
    self._end_of_line = end_of_line.encode(self._encoding)
    self._end_of_line_length = len(self._end_of_line)
    self._lines = []
    self._lines_buffer = b''
    self._lines_buffer_offset = 0
    self._current_offset = 0

  def __enter__(self):
    """Enters a with statement."""
    return self

  def __exit__(self, unused_type, unused_value, unused_traceback):
    """Exits a with statement."""
    # TODO: do we want to close the file_object here e.g. i.c.w. a flag value
    # to have TextFile manage the file_object?
    return

  def __iter__(self):
    """Returns a line of text.

    Yields:
      str: line of text.
    """
    line = self.readline()
    while line:
      yield line
      line = self.readline()

  # Note: that the following functions do not follow the style guide
  # because they are part of the readline file-like object interface.
  # pylint: disable=invalid-name

  def readline(self, size=None):
    """Reads a single line of text.

    The functions reads one entire line from the file-like object. A trailing
    end-of-line indicator (newline by default) is kept in the string (but may
    be absent when a file ends with an incomplete line). An empty string is
    returned only when end-of-file is encountered immediately.

    Args:
      size (Optional[int]): maximum byte size to read. If present and
          non-negative, it is a maximum byte count (including the trailing
          end-of-line) and an incomplete line may be returned.

    Returns:
      str: line of text.

    Raises:
      UnicodeDecodeError: if a line cannot be decoded and encoding errors is
          set to strict.
      ValueError: if the size is smaller than zero or exceeds the maximum
          (as defined by _MAXIMUM_READ_BUFFER_SIZE).
    """
    if size is not None and size < 0:
      raise ValueError('Invalid size value smaller than zero.')

    if size is not None and size > self._MAXIMUM_READ_BUFFER_SIZE:
      raise ValueError('Invalid size value exceeds maximum.')

    if not self._lines:
      if self._lines_buffer_offset >= self._file_object_size:
        return ''

      read_size = size
      if not read_size:
        read_size = self._MAXIMUM_READ_BUFFER_SIZE

      if self._lines_buffer_offset + read_size > self._file_object_size:
        read_size = self._file_object_size - self._lines_buffer_offset

      self._file_object.seek(self._lines_buffer_offset, os.SEEK_SET)
      read_buffer = self._file_object.read(read_size)

      self._lines_buffer_offset += len(read_buffer)

      self._lines = read_buffer.split(self._end_of_line)
      if self._lines_buffer:
        self._lines[0] = b''.join([self._lines_buffer, self._lines[0]])
        self._lines_buffer = b''

      # Move a partial line from the lines list to the lines buffer.
      if read_buffer[self._end_of_line_length:] != self._end_of_line:
        self._lines_buffer = self._lines.pop()

      for index, line in enumerate(self._lines):
        self._lines[index] = b''.join([line, self._end_of_line])

      if (self._lines_buffer and
          self._lines_buffer_offset >= self._file_object_size):
        self._lines.append(self._lines_buffer)
        self._lines_buffer = b''

    if not self._lines:
      line = self._lines_buffer
      self._lines_buffer = b''

    elif not size or size >= len(self._lines[0]):
      line = self._lines.pop(0)

    else:
      line = self._lines[0]
      self._lines[0] = line[size:]
      line = line[:size]

    last_offset = self._current_offset
    self._current_offset += len(line)

    decoded_line = line.decode(self._encoding, self._encoding_errors)

    # Remove a byte-order mark at the start of the file.
    if last_offset == 0 and decoded_line[0] == '\ufeff':
      decoded_line = decoded_line[1:]

    return decoded_line

  def readlines(self, sizehint=None):
    """Reads lines of text.

    The function reads until EOF using readline() and return a list containing
    the lines read.

    Args:
      sizehint (Optional[int]): maximum byte size to read. If present, instead
          of reading up to EOF, whole lines totalling sizehint bytes are read.

    Returns:
      list[str]: lines of text.
    """
    if sizehint is None or sizehint <= 0:
      sizehint = None

    lines = []
    lines_byte_size = 0
    line = self.readline()

    while line:
      lines.append(line)

      if sizehint is not None:
        lines_byte_size += len(line)

        if lines_byte_size >= sizehint:
          break

      line = self.readline()

    return lines

  # get_offset() is preferred above tell() by the libbfio layer used in libyal.
  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset into the file-like object.
    """
    return self._current_offset

  # Pythonesque alias for get_offset().
  def tell(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset into the file-like object.
    """
    return self._current_offset
