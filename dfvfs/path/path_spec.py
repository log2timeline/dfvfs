# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) path specification interface."""

from __future__ import unicode_literals

import abc


class PathSpec(object):
  """Path specification interface.

  Attributes:
    parent (PathSpec): parent path specification.
  """

  _IS_SYSTEM_LEVEL = False

  def __init__(self, parent=None, **kwargs):
    """Initializes a path specification.

    Args:
      parent (Optional[PathSpec]): parent path specification.
      kwargs (dict[str, object]): keyword arguments dependending on the path
          specification.

    Raises:
      ValueError: when there are unused keyword arguments.
    """
    if kwargs:
      raise ValueError('Unused keyword arguments: {0:s}.'.format(
          ', '.join(kwargs)))

    super(PathSpec, self).__init__()
    self.parent = parent

  def __eq__(self, other):
    """Determines if the path specification is equal to the other."""
    return isinstance(other, PathSpec) and self.comparable == other.comparable

  def __hash__(self):
    """Returns the hash of a path specification."""
    return hash(self.comparable)

  def _GetComparable(self, sub_comparable_string=''):
    """Retrieves the comparable representation.

    This is a convenience function for constructing comparables.

    Args:
      sub_comparable_string (str): sub comparable string.

    Returns:
      str: comparable representation of the path specification.
    """
    string_parts = []

    string_parts.append(getattr(self.parent, 'comparable', ''))
    string_parts.append('type: {0:s}'.format(self.type_indicator))

    if sub_comparable_string:
      string_parts.append(', {0:s}'.format(sub_comparable_string))
    string_parts.append('\n')

    return ''.join(string_parts)

  @abc.abstractproperty
  def comparable(self):
    """str: comparable representation of the path specification."""

  @property
  def type_indicator(self):
    """str: type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          'Invalid path specification missing type indicator.')
    return type_indicator

  def CopyToDict(self):
    """Copies the path specification to a dictionary.

    Returns:
      dict: path specification attributes.
    """
    path_spec_dict = {}
    for attribute_name, attribute_value in iter(self.__dict__.items()):
      if attribute_value is None:
        continue

      if attribute_name == 'parent':
        attribute_value = attribute_value.CopyToDict()

      path_spec_dict[attribute_name] = attribute_value

    return path_spec_dict

  def HasParent(self):
    """Determines if the path specification has a parent.

    Returns:
      bool: True if the path specification has a parent.
    """
    return self.parent is not None

  def IsSystemLevel(self):
    """Determines if the path specification is at system-level.

    System-level is an indication used if the path specification is
    handled by the operating system and should not have a parent.

    Returns:
      bool: True if the path specification is at system-level.
    """
    return getattr(self, '_IS_SYSTEM_LEVEL', False)
