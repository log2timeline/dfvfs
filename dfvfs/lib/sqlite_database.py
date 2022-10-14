# -*- coding: utf-8 -*-
"""Helper functions for SQLite database support."""

import os
import sqlite3
import tempfile


class SQLiteDatabaseFile(object):
  """SQLite database file using a file-like object."""

  _COPY_BUFFER_SIZE = 65536

  _HAS_COLUMN_QUERY = 'PRAGMA table_info("{0:s}")'

  _HAS_TABLE_QUERY = (
      'SELECT name FROM sqlite_master WHERE type = "table"')

  _HEADER_SIGNATURE = b'SQLite format 3'

  _NUMBER_OF_ROWS_QUERY = 'SELECT COUNT(*) FROM {0:s}'

  def __init__(self):
    """Initializes the database file object."""
    super(SQLiteDatabaseFile, self).__init__()
    self._column_names_per_table = {}
    self._connection = None
    self._cursor = None
    self._table_names = None
    self._temp_file_path = ''

  def Close(self):
    """Closes the database file object.

    Raises:
      IOError: if the close failed.
      OSError: if the close failed.
    """
    if self._connection:
      self._cursor = None
      self._connection.close()
      self._connection = None

    # TODO: move this to a central temp file manager and have it track errors.
    # https://github.com/log2timeline/dfvfs/issues/92
    try:
      os.remove(self._temp_file_path)
    except (IOError, OSError):
      pass

    self._temp_file_path = ''

  def GetNumberOfRows(self, table_name):
    """Retrieves the number of rows in the table.

    Args:
      table_name (str): name of the table.

    Returns:
      int: number of rows.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._connection:
      raise IOError('Not opened.')

    self._cursor.execute(self._NUMBER_OF_ROWS_QUERY.format(table_name))
    row = self._cursor.fetchone()
    if not row:
      raise IOError(
          f'Unable to retrieve number of rows of table: {table_name:s}')

    number_of_rows = row[0]
    if isinstance(number_of_rows, str):
      try:
        number_of_rows = int(number_of_rows, 10)
      except ValueError as exception:
        raise IOError((
            f'Unable to determine number of rows of table: {table_name:s} with '
            f'error: {exception!s}'))

    return number_of_rows

  def HasColumn(self, table_name, column_name):
    """Determines if a specific column exists.

    Args:
      table_name (str): name of the table.
      column_name (str): name of the column.

    Returns:
      bool: True if the column exists.

    Raises:
      IOError: if the database file is not opened.
      OSError: if the database file is not opened.
    """
    if not self._connection:
      raise IOError('Not opened.')

    if not column_name:
      return False

    table_name = table_name.lower()
    column_names = self._column_names_per_table.get(table_name, None)
    if column_names is None:
      column_names = []

      self._cursor.execute(self._HAS_COLUMN_QUERY.format(table_name))
      for row in self._cursor.fetchall():
        if not row[1]:
          continue

        row_column_name = row[1]
        if isinstance(row_column_name, bytes):
          row_column_name = row_column_name.decode('utf-8')

        column_names.append(row_column_name.lower())

      self._column_names_per_table[table_name] = column_names

    column_name = column_name.lower()
    return column_name in column_names

  def HasTable(self, table_name):
    """Determines if a specific table exists.

    Args:
      table_name (str): name of the table.

    Returns:
      bool: True if the column exists.

    Raises:
      IOError: if the database file is not opened.
      OSError: if the database file is not opened.
    """
    if not self._connection:
      raise IOError('Not opened.')

    if not table_name:
      return False

    if self._table_names is None:
      self._table_names = []

      self._cursor.execute(self._HAS_TABLE_QUERY)
      for row in self._cursor.fetchall():
        if not row[0]:
          continue

        row_table_name = row[0]
        if isinstance(row_table_name, bytes):
          row_table_name = row_table_name.decode('utf-8')

        self._table_names.append(row_table_name.lower())

    table_name = table_name.lower()
    return table_name in self._table_names

  def Open(self, file_object):
    """Opens the database file object.

    Args:
      file_object (FileIO): file-like object.

    Raises:
      IOError: if the SQLite database signature does not match.
      OSError: if the SQLite database signature does not match.
      ValueError: if the file-like object is invalid.
    """
    if not file_object:
      raise ValueError('Missing file-like object.')

    # Since pysqlite3 does not provide an exclusive read-only mode and
    # cannot interact with a file-like object directly we make a temporary
    # copy. Before making a copy we check the header signature.

    file_object.seek(0, os.SEEK_SET)
    data = file_object.read(len(self._HEADER_SIGNATURE))

    if data != self._HEADER_SIGNATURE:
      raise IOError('Unsupported SQLite database signature.')

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
      self._temp_file_path = temp_file.name
      while data:
        temp_file.write(data)
        data = file_object.read(self._COPY_BUFFER_SIZE)

    self._connection = sqlite3.connect(self._temp_file_path)
    self._connection.text_factory = bytes
    self._cursor = self._connection.cursor()

  def Query(self, query, parameters=None):
    """Queries the database file.

    Args:
      query (str): SQL query.
      parameters (Optional[dict|tuple]): query parameters.

    Returns:
      list[sqlite3.Row]: rows resulting from the query.
    """
    # TODO: catch Warning and return None.
    # Note that we cannot pass parameters as a keyword argument here.
    # A parameters value of None is not supported.
    if parameters:
      self._cursor.execute(query, parameters)
    else:
      self._cursor.execute(query)

    return self._cursor.fetchall()
