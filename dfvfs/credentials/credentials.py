# -*- coding: utf-8 -*-
"""The credentials interface."""


class Credentials(object):
  """Credentials interface."""

  def __init__(self):
    """Initializes credentials.

    Raises:
      ValueError: if a derived credentials class does not define a type
          indicator.
    """
    super(Credentials, self).__init__()

    if not getattr(self, 'TYPE_INDICATOR', None):
      raise ValueError('Missing type indicator.')

  @property
  def type_indicator(self):
    """str: type indicator."""
    # pylint: disable=no-member
    return self.TYPE_INDICATOR
