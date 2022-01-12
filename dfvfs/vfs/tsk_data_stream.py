# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) data stream implementation."""

import pytsk3

from dfvfs.vfs import data_stream


class TSKDataStream(data_stream.DataStream):
  """File system data stream that uses pytsk3."""

  def __init__(self, file_system, pytsk_attribute):
    """Initializes a data stream.

    Args:
      file_system (TSKFileSystem): file system.
      pytsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKDataStream, self).__init__()
    self._file_system = file_system
    self._tsk_attribute = pytsk_attribute

  @property
  def name(self):
    """str: name."""
    if self._tsk_attribute:
      # The value of the attribute name will be None for the default
      # data stream.
      attribute_name = getattr(self._tsk_attribute.info, 'name', None)
      if attribute_name:
        try:
          # pytsk3 returns an UTF-8 encoded byte string.
          return attribute_name.decode('utf8')
        except UnicodeError:
          pass

    return ''

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream, false if not.
    """
    if not self._tsk_attribute or not self._file_system:
      return True

    if self._file_system.IsHFS():
      attribute_type = getattr(self._tsk_attribute.info, 'type', None)
      return attribute_type in (
          pytsk3.TSK_FS_ATTR_TYPE_HFS_DEFAULT, pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA)

    if self._file_system.IsNTFS():
      return not bool(self.name)

    return True
