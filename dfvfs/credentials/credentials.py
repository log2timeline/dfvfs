# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) credentials object interface."""


class Credentials(object):
  """Class that implements the credentials object interface."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, u'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid resolver helper missing type indicator.')
    return type_indicator
