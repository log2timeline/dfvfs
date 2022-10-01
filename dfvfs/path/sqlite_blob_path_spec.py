# -*- coding: utf-8 -*-
"""The SQLite blob path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class SQLiteBlobPathSpec(path_spec.PathSpec):
  """SQLite blob file path specification.

  Attributes:
    column_name (str): name of the column in which the blob is stored.
    row_condition (tuple): condition of the row in which the blob is stored.
        The condition is a tuple in the form: (column_name, operator, value).
        The condition must yield a single result.
    row_index (int): index of the row in which the blob is stored.
    table_name (str): name of the table in which the blob is stored.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def __init__(
      self, column_name=None, parent=None, row_condition=None,
      row_index=None, table_name=None, **kwargs):
    """Initializes a path specification.

    Note that the SQLite blob file path specification must have a parent.

    Args:
      column_name (Optional[str]): name of the column in which the blob is
          stored.
      parent (Optional[PathSpec]): parent path specification.
      row_condition (Optional[tuple]): condition of the row in which the blob
          is stored. The condition is a tuple in the form: (column_name,
          operator, value).  The condition must yield a single result.
      row_index (Optional[int]): index of the row in which the blob is stored.
      table_name (Optional[str]): name of the table in which the blob is
          stored.

    Raises:
      ValueError: when table_name, column_name, row_condition and row_index,
          or parent is not set.
    """
    if not table_name or not column_name or not parent:
      raise ValueError('Missing table_name, column_name or parent value.')

    if (row_condition and (
        not isinstance(row_condition, tuple) or len(row_condition) != 3)):
      raise ValueError((
          'Unsupported row_condition not a tuple in the form: '
          '(column_name, operator, value).'))

    super(SQLiteBlobPathSpec, self).__init__(parent=parent, **kwargs)
    self.column_name = column_name
    self.row_condition = row_condition
    self.row_index = row_index
    self.table_name = table_name

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    string_parts = []

    string_parts.append(f'table name: {self.table_name:s}')
    string_parts.append(f'column name: {self.column_name:s}')

    if self.row_condition is not None:
      row_condition_string = ' '.join([
          f'{value!s}' for value in self.row_condition])
      string_parts.append(f'row condition: "{row_condition_string:s}"')

    if self.row_index is not None:
      string_parts.append(f'row index: {self.row_index:d}')

    return self._GetComparable(sub_comparable_string=', '.join(string_parts))


factory.Factory.RegisterPathSpec(SQLiteBlobPathSpec)
