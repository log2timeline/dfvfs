# -*- coding: utf-8 -*-
"""The compression manager."""

from __future__ import unicode_literals


class CompressionManager(object):
  """Compression manager."""

  _decompressors = {}

  @classmethod
  def DeregisterDecompressor(cls, decompressor):
    """Deregisters a decompressor for a specific compression method.

    Args:
      decompressor (type): decompressor class.

    Raises:
      KeyError: if the corresponding decompressor is not set.
    """
    compression_method = decompressor.COMPRESSION_METHOD.lower()
    if compression_method not in cls._decompressors:
      raise KeyError(
          'Decompressor for compression method: {0:s} not set.'.format(
              decompressor.COMPRESSION_METHOD))

    del cls._decompressors[compression_method]

  @classmethod
  def GetDecompressor(cls, compression_method):
    """Retrieves the decompressor object for a specific compression method.

    Args:
      compression_method (str): compression method identifier.

    Returns:
      Decompressor: decompressor or None if the compression method does
          not exists.
    """
    compression_method = compression_method.lower()
    decompressor = cls._decompressors.get(compression_method, None)
    if not decompressor:
      return None

    return decompressor()

  @classmethod
  def RegisterDecompressor(cls, decompressor):
    """Registers a decompressor for a specific compression method.

    Args:
      decompressor (type): decompressor class.

    Raises:
      KeyError: if the corresponding decompressor is already set.
    """
    compression_method = decompressor.COMPRESSION_METHOD.lower()
    if compression_method in cls._decompressors:
      raise KeyError(
          'Decompressor for compression method: {0:s} already set.'.format(
              decompressor.COMPRESSION_METHOD))

    cls._decompressors[compression_method] = decompressor

  @classmethod
  def RegisterDecompressors(cls, decompressors):
    """Registers decompressors.

    The decompressors are identified based on their lower case compression
    method.

    Args:
      decompressors (list[type]): decompressor classes.

    Raises:
      KeyError: if decompressor is already set for the corresponding
                compression method.
    """
    for decompressor in decompressors:
      cls.RegisterDecompressor(decompressor)
