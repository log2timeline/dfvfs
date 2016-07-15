# -*- coding: utf-8 -*-
"""The decompressor object interface."""

import abc


class Decompressor(object):
  """Class that implements the decompressor object interface."""

  @abc.abstractmethod
  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data (bytes): compressed data.

    Returns:
      tuple(bytes,bytes): uncompressed data and remaining compressed data.
    """
