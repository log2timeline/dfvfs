# -*- coding: utf-8 -*-
"""The path specification resolver helper manager."""

from __future__ import unicode_literals


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
      raise KeyError(
          'Resolver helper object not set for type indicator: {0:s}.'.format(
              resolver_helper.type_indicator))

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
          'Resolver helper not set for type indicator: {0:s}.'.format(
              type_indicator))

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
          'Resolver helper object already set for type indicator: '
          '{0!s}.').format(resolver_helper.type_indicator))

    cls._resolver_helpers[resolver_helper.type_indicator] = resolver_helper
