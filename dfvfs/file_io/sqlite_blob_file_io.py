# -*- coding: utf-8 -*-
"""The SQlite blob file-like object."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import sqlite_database
from dfvfs.resolver import resolver


class SQLiteBlobFile(file_io.FileIO):
  """File input/output (IO) object using sqlite."""

  _OPERATORS = frozenset(['==', '=', 'IS'])

  def __init__(self, resolver_context, path_spec):
    """Initializes the file-like object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(SQLiteBlobFile, self).__init__(resolver_context, path_spec)
    self._blob = None
    self._current_offset = 0
    self._database_object = None
    self._number_of_rows = None
    self._size = 0
    self._table_name = None

  def _Close(self):
    """Closes the file-like object."""
    if self._database_object:
      self._database_object.Close()

    self._blob = None
    self._current_offset = 0
    self._size = 0
    self._table_name = None

  def _Open(self, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    table_name = getattr(self._path_spec, 'table_name', None)
    if table_name is None:
      raise errors.PathSpecError('Path specification missing table name.')

    column_name = getattr(self._path_spec, 'column_name', None)
    if column_name is None:
      raise errors.PathSpecError('Path specification missing column name.')

    row_condition = getattr(self._path_spec, 'row_condition', None)
    if row_condition:
      if not isinstance(row_condition, tuple) or len(row_condition) != 3:
        raise errors.PathSpecError((
            'Unsupported row_condition not a tuple in the form: '
            '(column_name, operator, value).'))

    row_index = getattr(self._path_spec, 'row_index', None)
    if row_index is not None and not isinstance(row_index, int):
      raise errors.PathSpecError('Unsupported row_index not of integer type.')

    if not row_condition and row_index is None:
      raise errors.PathSpecError(
          'Path specification requires either a row_condition or row_index.')

    if self._database_object:
      raise IOError('Database file already set.')

    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    database_object = sqlite_database.SQLiteDatabaseFile()
    database_object.Open(file_object)

    # Sanity check the table and column names.
    error_string = ''
    if not database_object.HasTable(table_name):
      error_string = f'Missing table: {table_name:s}'

    elif not database_object.HasColumn(table_name, column_name):
      error_string = (
          f'Missing column: {column_name:s} in table: {table_name:s}')

    elif not row_condition:
      query = (f'SELECT {column_name:s} FROM {table_name:s} LIMIT 1 '
               f'OFFSET {row_index:d}')
      rows = database_object.Query(query)

    elif not database_object.HasColumn(table_name, row_condition[0]):
      condition_column_name = row_condition[0]
      error_string = (
          f'Missing row condition column: {condition_column_name:s} in table: '
          f'{table_name:s}')

    elif row_condition[1] not in self._OPERATORS:
      condition_operator = row_condition[1]
      error_string = (
          f'Unsupported row condition operator: {condition_operator:s}.')

    else:
      condition_column_name = row_condition[0]
      condition_operator = row_condition[1]
      query = (f'SELECT {column_name:s} FROM {table_name:s} '
               f'WHERE {condition_column_name:s} {condition_operator:s} ?')
      rows = database_object.Query(query, parameters=(row_condition[2], ))

    # Make sure the query returns a single row, using cursor.rowcount
    # is not reliable for this purpose.
    if not error_string and (len(rows) != 1 or len(rows[0]) != 1):
      if not row_condition:
        error_string = (
            f'Unable to open blob in table: {table_name:s} and column: '
            f'{column_name:s} for row: {row_index:d}.')

      else:
        row_condition_string = ' '.join([
            f'{value!s}' for value in iter(row_condition)])
        error_string = (
            f'Unable to open blob in table: {table_name:s} and column: '
            f'{column_name:s} where: {row_condition_string:s}.')

    if error_string:
      database_object.Close()
      raise IOError(error_string)

    self._blob = rows[0][0]
    self._current_offset = 0
    self._database_object = database_object
    self._size = len(self._blob)
    self._table_name = table_name

  # TODO: remove this when there is a move this to a central temp file
  # manager. https://github.com/log2timeline/dfvfs/issues/92
  def GetNumberOfRows(self):
    """Retrieves the number of rows of the table.

    Returns:
      int: number of rows.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._database_object:
      raise IOError('Not opened.')

    if self._number_of_rows is None:
      self._number_of_rows = self._database_object.GetNumberOfRows(
          self._table_name)

    return self._number_of_rows

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
    if not self._database_object:
      raise IOError('Not opened.')

    if self._current_offset < 0:
      raise IOError('Invalid offset value out of bounds.')

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
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
      OSError: if the seek failed.
    """
    if not self._database_object:
      raise IOError('Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value out of bounds.')

    self._current_offset = offset

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._database_object:
      raise IOError('Not opened.')

    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._database_object:
      raise IOError('Not opened.')

    return self._size
