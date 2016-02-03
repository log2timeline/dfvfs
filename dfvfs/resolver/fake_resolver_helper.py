# -*- coding: utf-8 -*-
"""The fake path specification resolver helper implementation."""

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class FakeResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the fake resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  # The fake file system resolver has no implementation and
  # should raise RuntimeError.


resolver.Resolver.RegisterHelper(FakeResolverHelper())
