# -*- coding: utf-8 -*-
"""The SQlite blob file-like object."""

import os
import tempfile

try:
  from pysqlite2 import dbapi2 as sqlite3
except ImportError:
  import sqlite3

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class SQLiteBlobFile(file_io.FileIO):
  """Class that implements a file-like object using sqlite."""

  _COPY_BUFFER_SIZE = 65536
  _HEADER_SIGNATURE = b'SQLite format 3'

  _HAS_COLUMN_QUERY = u'PRAGMA table_info("{0:s}")'

  _HAS_TABLE_QUERY = (
      u'SELECT name FROM sqlite_master WHERE type = "table"')

  _NUMBER_OF_ROWS_QUERY = u'SELECT COUNT(*) FROM {0:s}'

  _OPERATORS = frozenset([u'==', u'=', u'IS'])

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(SQLiteBlobFile, self).__init__(resolver_context)
    self._blob = None
    self._connection = None
    self._current_offset = 0
    self._cursor = None
    self._number_of_rows = None
    self._size = 0
    self._temp_file_path = u''

  def _Close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """
    if self._connection:
      self._cursor = None
      self._connection.close()
      self._connection = None

    self._blob = None
    self._current_offset = 0
    self._size = 0

    # TODO: move this to a central temp file manager and have it track errors.
    try:
      os.remove(self._temp_file_path)
    except (OSError, IOError):
      pass

    self._temp_file_path = u''

  def _HasColumn(self, table_name, column_name):
    """Determines if a specific column exists.

    Args:
      table_name: the table name.
      column_name: the column name.

    Returns:
      True if the column exists, false otheriwse.

    Raises:
      IOError: if the data base is not opened.
    """
    if not self._connection:
      raise IOError(u'Not opened.')

    if not column_name:
      return False

    column_name = column_name.lower()
    self._cursor.execute(self._HAS_COLUMN_QUERY.format(table_name))

    for row in self._cursor.fetchall():
      # As a sanity check we compare the column name in Python instead of
      # passing it as part of the SQL query.
      if row[1] and row[1].lower() == column_name:
        return True

    return False

  def _HasTable(self, table_name):
    """Determines if a specific table exists.

    Args:
      table_name: the table name.

    Returns:
      True if the table exists, false otheriwse.

    Raises:
      IOError: if the data base is not opened.
    """
    if not self._connection:
      raise IOError(u'Not opened.')

    if not table_name:
      return False

    table_name = table_name.lower()
    self._cursor.execute(self._HAS_TABLE_QUERY)

    for row in self._cursor.fetchall():
      # As a sanity check we compare the table name in Python instead of
      # passing it as part of the SQL query.
      if row[0] and row[0].lower() == table_name:
        return True

    return False

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specfication.')

    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    table_name = getattr(path_spec, u'table_name', None)
    if table_name is None:
      raise errors.PathSpecError(u'Path specification missing table name.')

    column_name = getattr(path_spec, u'column_name', None)
    if column_name is None:
      raise errors.PathSpecError(u'Path specification missing column name.')

    row_condition = getattr(path_spec, u'row_condition', None)
    if row_condition:
      if not isinstance(row_condition, tuple) or len(row_condition) != 3:
        raise errors.PathSpecError((
            u'Unsupported row_condition not a tuple in the form: '
            u'(column_name, operator, value).'))

    row_index = getattr(path_spec, u'row_index', None)
    if row_index is not None:
      if not isinstance(row_index, (int, long)):
        raise errors.PathSpecError(
            u'Unsupported row_index not of integer type.')

    if self._connection:
      raise IOError(u'Connection already set.')

    # Since pysqlite3 does not provide an exclusive read-only mode and
    # cannot interact with a file-like object directly we make a temporary
    # copy. Before making a copy we check the header signature.

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    file_object.seek(0, os.SEEK_SET)
    data = file_object.read(len(self._HEADER_SIGNATURE))

    if data != self._HEADER_SIGNATURE:
      file_object.close()
      raise IOError(u'Unsupported SQLite database signature.')

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
      self._temp_file_path = temp_file.name
      while data:
        temp_file.write(data)
        data = file_object.read(self._COPY_BUFFER_SIZE)

    file_object.close()

    self._connection = sqlite3.connect(self._temp_file_path)
    self._connection.text_factory = bytes
    self._cursor = self._connection.cursor()

    # Sanity check the table and column names.
    if not self._HasTable(table_name):
      self._connection.close()
      raise IOError(u'Missing table: {0:s}'.format(table_name))

    if not self._HasColumn(table_name, column_name):
      self._connection.close()
      raise IOError(u'Missing column: {0:s} in table: {1:s}'.format(
          column_name, table_name))

    if row_condition:
      if not self._HasColumn(table_name, row_condition[0]):
        self._connection.close()
        raise IOError(
            u'Missing row condition column: {0:s} in table: {1:s}'.format(
                row_condition[0], table_name))

      if row_condition[1] not in self._OPERATORS:
        self._connection.close()
        raise IOError(
            u'Unsupported row condition operator: {0:s}.'.format(
                row_condition[1]))

      query = u'SELECT {0:s} FROM {1:s} WHERE {2:s} {3:s} ?'.format(
          column_name, table_name, row_condition[0], row_condition[1])
      self._cursor.execute(query, (row_condition[2], ))

    else:
      query = u'SELECT {0:s} FROM {1:s} LIMIT 1 OFFSET {2:d}'.format(
          column_name, table_name, row_index)
      self._cursor.execute(query)

    # Make sure the query returns a single row, using cursor.rowcount
    # is not reliable for this purpose.
    rows = self._cursor.fetchall()
    if len(rows) != 1 or len(rows[0]) != 1:
      if row_condition:
        row_condition_string = u' '.join([
            u'{0!s}'.format(value) for value in row_condition])
        error_string = (
            u'Unable to open blob in table: {0:s} and column: {1:s} '
            u'where: {2:s}.').format(
                table_name, column_name, row_condition_string)

      else:
        error_string = (
            u'Unable to open blob in table: {0:s} and column: {1:s} '
            u'for row: {2:d}.').format(table_name, column_name, row_index)

      self._Close()
      raise IOError(error_string)

    self._blob = rows[0][0]
    self._current_offset = 0
    self._size = len(self._blob)

    # Get number of rows for this table
    self._cursor.execute(self._NUMBER_OF_ROWS_QUERY.format(table_name))
    self._number_of_rows = int(self._cursor.fetchone()[0])

  def GetNumberOfRows(self):
    """Returns the number of rows the table has.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._connection:
      raise IOError(u'Not opened.')

    return self._number_of_rows

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

       The function will read a byte string of the specified size or
       all of the remaining data if no size was specified.

    Args:
      size: Optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._connection:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(u'Invalid offset value out of bounds.')

    if size == 0 or self._current_offset >= self._size:
      return b''

    if size is None:
      size = self._size
    if self._current_offset + size > self._size:
      size = self._size - self._current_offset

    start_offset = self._current_offset
    self._current_offset += size
    return self._blob[start_offset:self._current_offset]

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._connection:
      raise IOError(u'Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')

    if offset < 0:
      raise IOError(u'Invalid offset value out of bounds.')

    self._current_offset = offset

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._connection:
      raise IOError(u'Not opened.')

    return self._current_offset

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._connection:
      raise IOError(u'Not opened.')

    return self._size
