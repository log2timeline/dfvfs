# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) serializer object interfaces."""

import abc


class PathSpecSerializer(object):
  """Path specification serializer interface."""

  # Since abc does not seem to have an @abc.abstractclassmethod we're using
  # @abc.abstractmethod instead and shutting up pylint about:
  # E0213: Method should have "self" as first argument.
  # pylint: disable=no-self-argument,redundant-returns-doc

  @abc.abstractmethod
  def ReadSerialized(cls, serialized):
    """Reads a path specification from serialized form.

    Args:
      serialized (object): serialized form of the path specification.

    Returns:
      PathSpec: a path specification.
    """

  @abc.abstractmethod
  def WriteSerialized(cls, path_spec):
    """Writes a path specification to serialized form.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      object: serialized form of the path specification.
    """
