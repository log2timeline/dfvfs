# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) path specification object interface."""

import abc


class PathSpec(object):
  """Class that implements the path specification object interface.

  Attributes:
    parent: parent path specification (instance of PathSpec).
  """

  _IS_SYSTEM_LEVEL = False

  def __init__(self, parent=None, **kwargs):
    """Initializes the path specification object.

    Args:
      parent: optional parent path specification (instance of PathSpec).
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
    return isinstance(other, PathSpec) and self.comparable == other.comparable

  def __hash__(self):
    """Returns the hash of a path specification."""
    return hash(self.comparable)

  def _GetComparable(self, sub_comparable_string=u''):
    """Retrieves the comparable representation.

    This is a convenience function for constructing comparables.

    Args:
      sub_comparable_string: the sub comparable string.

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

  def CopyToDict(self):
    """Copies the path specification to a dictionary.

    Returns:
      A dictionary containing the path specification attributes.
    """
    path_spec_dict = {}
    for attribute_name, attribute_value in iter(self.__dict__.items()):
      if attribute_value is None:
        continue

      if attribute_name == u'parent':
        attribute_value = attribute_value.CopyToDict()

      path_spec_dict[attribute_name] = attribute_value

    return path_spec_dict

  def HasParent(self):
    """Determines if the path specification has a parent."""
    return self.parent is not None

  def IsSystemLevel(self):
    """Determines if the path specification is at system-level."""
    return getattr(self, u'_IS_SYSTEM_LEVEL', False)
