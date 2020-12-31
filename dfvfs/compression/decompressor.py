# -*- coding: utf-8 -*-
"""The decompressor interface."""

import abc


class Decompressor(object):
  """Decompressor interface."""

  # pylint: disable=redundant-returns-doc

  @abc.abstractmethod
  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data (bytes): compressed data.

    Returns:
      tuple(bytes, bytes): uncompressed data and remaining compressed data.
    """
