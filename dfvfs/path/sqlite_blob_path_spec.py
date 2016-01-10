# -*- coding: utf-8 -*-
"""The SQLite blob path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import path_spec


class SQLiteBlobPathSpec(path_spec.PathSpec):
  """Class that implements the SQLite blob file path specification.

  Attributes:
    column_name: string containing the name of the column in which the blob
                 is stored.
    row_condition: condition of the row in which the blob is stored.
                   The condition is a tuple in the form:
                   (column_name, operator, value).
                   The condition must yield a single result.
    row_index: integer containing index of the row in which the blob is stored.
    table_name: string containing the name of the table in which the blob
                is stored.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def __init__(
      self, column_name=None, parent=None, row_condition=None,
      row_index=None, table_name=None, **kwargs):
    """Initializes the path specification object.

    Note that the SQLite blob file path specification must have a parent.

    Args:
      column_name: optional string containing the name of the column in which
                   the blob is stored.
      parent: optional parent path specification (instance of PathSpec).
      row_condition: optional condition of the row in which the blob is stored.
                     The condition is a tuple in the form:
                     (column_name, operator, value).
                     The condition must yield a single result.
      row_index: optional integer containing index of the row in which the
                 blob is stored.
      table_name: optional string containing the name of the table in which
                  the blob is stored.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification

    Raises:
      ValueError: when table_name, column_name, row_condition and row_index,
                  or parent is not set.
    """
    if not table_name or not column_name or not parent:
      raise ValueError(u'Missing table_name, column_name or parent value.')

    if (row_condition and (
        not isinstance(row_condition, tuple) or len(row_condition) != 3)):
      raise ValueError((
          u'Unsupported row_condition not a tuple in the form: '
          u'(column_name, operator, value).'))

    super(SQLiteBlobPathSpec, self).__init__(parent=parent, **kwargs)
    self.table_name = table_name
    self.column_name = column_name
    self.row_condition = row_condition
    self.row_index = row_index

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    string_parts.append(u'table name: {0:s}'.format(self.table_name))
    string_parts.append(u'column name: {0:s}'.format(self.column_name))

    if self.row_condition is not None:
      row_condition_string = u' '.join([
          u'{0!s}'.format(value) for value in self.row_condition])
      string_parts.append(u'row condition: "{0:s}"'.format(
          row_condition_string))

    if self.row_index is not None:
      string_parts.append(u'row index: {0:d}'.format(self.row_index))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(SQLiteBlobPathSpec)
