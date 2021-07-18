# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) attribute interface."""


class Attribute(object):
  """Attribute interface."""

  @property
  def type_indicator(self):
    """str: type indicator or None if not known."""
    return getattr(self, 'TYPE_INDICATOR', None)
