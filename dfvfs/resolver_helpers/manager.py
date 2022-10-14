# -*- coding: utf-8 -*-
"""The path specification resolver helper manager."""


class ResolverHelperManager(object):
  """Path specification resolver helper manager."""

  _resolver_helpers = {}

  @classmethod
  def DeregisterHelper(cls, resolver_helper):
    """Deregisters a path specification resolver helper.

    Args:
      resolver_helper (ResolverHelper): resolver helper.

    Raises:
      KeyError: if resolver helper object is not set for the corresponding
          type indicator.
    """
    if resolver_helper.type_indicator not in cls._resolver_helpers:
      raise KeyError((
          f'Resolver helper object not set for type indicator: '
          f'{resolver_helper.type_indicator:s}.'))

    del cls._resolver_helpers[resolver_helper.type_indicator]

  @classmethod
  def GetHelper(cls, type_indicator):
    """Retrieves the path specification resolver helper for the specified type.

    Args:
      type_indicator (str): type indicator.

    Returns:
      ResolverHelper: a resolver helper.

    Raises:
      KeyError: if resolver helper is not set for the corresponding type
          indicator.
    """
    if type_indicator not in cls._resolver_helpers:
      raise KeyError(
          f'Resolver helper not set for type indicator: {type_indicator:s}.')

    return cls._resolver_helpers[type_indicator]

  @classmethod
  def RegisterHelper(cls, resolver_helper):
    """Registers a path specification resolver helper.

    Args:
      resolver_helper (ResolverHelper): resolver helper.

    Raises:
      KeyError: if resolver helper object is already set for the corresponding
          type indicator.
    """
    if resolver_helper.type_indicator in cls._resolver_helpers:
      raise KeyError((
          f'Resolver helper object already set for type indicator: '
          f'{resolver_helper.type_indicator!s}.'))

    cls._resolver_helpers[resolver_helper.type_indicator] = resolver_helper
