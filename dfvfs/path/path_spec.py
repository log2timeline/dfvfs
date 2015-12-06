# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) path specification object interface."""

import abc


class PathSpec(object):
  """Class that implements the path specification object interface."""

  _IS_SYSTEM_LEVEL = False

  def __init__(self, parent=None, **kwargs):
    """Initializes the path specification object.

    Args:
      parent: optional parent path specification (instance of PathSpec),
              default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.

    Raises:
      ValueError: when there are unused keyword arguments.
    """
    if kwargs:
      raise ValueError(u'Unused keyword arguments: {0:s}.'.format(
          u', '.join(kwargs)))

    super(PathSpec, self).__init__()
    self.parent = parent

  def __eq__(self, other):
    """Determines if the path specification is equal to the other."""
    return self.comparable == other.comparable

  def __hash__(self):
    """Returns the hash of a path specification."""
    return hash(self.comparable)

  def _GetComparable(self, sub_comparable_string=u''):
    """Retrieves the comparable representation.

       This is a convenince function for constructing comparables.

    Args:
      sub_comparable_string: the sub comparable string. The default is
                             an empty string.

    Returns:
      A string containing the comparable.
    """
    string_parts = []

    string_parts.append(getattr(self.parent, u'comparable', u''))
    string_parts.append(u'type: {0:s}'.format(self.type_indicator))

    if sub_comparable_string:
      string_parts.append(u', {0:s}'.format(sub_comparable_string))
    string_parts.append(u'\n')

    return u''.join(string_parts)

  @abc.abstractproperty
  def comparable(self):
    """Comparable representation of the path specification."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, u'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid path specification missing type indicator.')
    return type_indicator

  def HasParent(self):
    """Determines if the path specfication has a parent."""
    return self.parent is not None

  def IsSystemLevel(self):
    """Determines if the path specfication is at system-level."""
    return getattr(self, u'_IS_SYSTEM_LEVEL', False)
