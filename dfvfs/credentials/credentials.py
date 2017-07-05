# -*- coding: utf-8 -*-
"""The credentials interface."""

from __future__ import unicode_literals


class Credentials(object):
  """Credentials interface."""

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          'Invalid resolver helper missing type indicator.')
    return type_indicator
