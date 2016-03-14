# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) serializer object interfaces."""

# Since abc does not seem to have an @abc.abstractclassmethod we're using
# @abc.abstractmethod instead and shutting up pylint about:
# E0213: Method should have "self" as first argument.
# pylint: disable=no-self-argument

import abc


class PathSpecSerializer(object):
  """Class that implements the path specification serializer interface."""

  @abc.abstractmethod
  def ReadSerialized(cls, serialized):
    """Reads a path specification from serialized form.

    Args:
      serialized: an object containing the serialized form.

    Returns:
      A path specification (instance of PathSpec).
    """

  @abc.abstractmethod
  def WriteSerialized(cls, path_spec):
    """Writes a path specification to serialized form.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      An object containing the serialized form.
    """
