# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) attribute implementation."""

from dfvfs.vfs import attribute


class TSKAttribute(attribute.Attribute):
  """File system attribute that uses pytsk3."""

  def __init__(self, pytsk_attribute):
    """Initializes an attribute.

    Args:
      pytsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKAttribute, self).__init__()
    self._tsk_attribute = pytsk_attribute

  @property
  def attribute_type(self):
    """object: attribute type."""
    return getattr(self._tsk_attribute.info, 'type', None)
