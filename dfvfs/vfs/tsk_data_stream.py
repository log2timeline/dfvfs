# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) data stream implementation."""

import pytsk3

from dfvfs.vfs import data_stream


class TSKDataStream(data_stream.DataStream):
  """File system data stream that uses pytsk3."""

  def __init__(self, pytsk_attribute):
    """Initializes a data stream.

    Args:
      pytsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKDataStream, self).__init__()
    self._name = ''

    if pytsk_attribute:
      # The value of the attribute name will be None for the default
      # data stream.
      attribute_name = getattr(pytsk_attribute.info, 'name', None)
      attribute_type = getattr(pytsk_attribute.info, 'type', None)
      if attribute_type == pytsk3.TSK_FS_ATTR_TYPE_HFS_RSRC:
        self._name = 'rsrc'

      elif attribute_name:
        try:
          # pytsk3 returns an UTF-8 encoded byte string.
          self._name = attribute_name.decode('utf8')
        except UnicodeError:
          pass

  @property
  def name(self):
    """str: name."""
    return self._name

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream, false if not.
    """
    return not bool(self._name)
