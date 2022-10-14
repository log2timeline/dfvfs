# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) path specification interface."""

from dfvfs.lib import definitions


class PathSpec(object):
  """Path specification interface.

  Attributes:
    parent (PathSpec): parent path specification.
  """

  # pylint: disable=missing-raises-doc

  _IS_SYSTEM_LEVEL = False

  def __init__(self, parent=None, **kwargs):
    """Initializes a path specification.

    Args:
      parent (Optional[PathSpec]): parent path specification.
      kwargs (dict[str, object]): keyword arguments depending on the path
          specification.

    Raises:
      ValueError: if a derived path specification class does not define a type
          indicator or when there are unused keyword arguments.
    """
    if kwargs:
      keyword_arguments = ', '.join(kwargs)
      raise ValueError(f'Unused keyword arguments: {keyword_arguments:s}.')

    super(PathSpec, self).__init__()
    self.parent = parent

    if not getattr(self, 'TYPE_INDICATOR', None):
      raise ValueError('Missing type indicator.')

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
    string_parts.append(f'type: {self.type_indicator:s}')

    if sub_comparable_string:
      string_parts.append(f', {sub_comparable_string:s}')
    string_parts.append('\n')

    return ''.join(string_parts)

  @property
  def comparable(self):
    """str: comparable representation of the path specification."""
    return self._GetComparable()

  @property
  def type_indicator(self):
    """str: type indicator."""
    # pylint: disable=no-member
    return self.TYPE_INDICATOR

  def CopyToDict(self):
    """Copies the path specification to a dictionary.

    Returns:
      dict[str, object]: path specification attributes.
    """
    path_spec_dict = {}
    for attribute_name, attribute_value in self.__dict__.items():
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

  def IsFileSystem(self):
    """Determines if the path specification is a file system.

    Returns:
      bool: True if the path specification is a file system.
    """
    return self.type_indicator in definitions.FILE_SYSTEM_TYPE_INDICATORS

  def IsSystemLevel(self):
    """Determines if the path specification is at system-level.

    System-level is an indication used if the path specification is
    handled by the operating system and should not have a parent.

    Returns:
      bool: True if the path specification is at system-level.
    """
    return getattr(self, '_IS_SYSTEM_LEVEL', False)

  def IsVolumeSystem(self):
    """Determines if the path specification is a volume system.

    Returns:
      bool: True if the path specification is a volume system.
    """
    return self.type_indicator in definitions.VOLUME_SYSTEM_TYPE_INDICATORS

  def IsVolumeSystemRoot(self):
    """Determines if the path specification is the root of a volume system.

    Returns:
      bool: True if the path specification is the root of a volume system.
    """
    return self.IsVolumeSystem() and getattr(self, 'location', None) == '/'
