# -*- coding: utf-8 -*-
"""The decompressor object interface."""

import abc


class Decompressor(object):
  """Class that implements the decompressor object interface."""

  @abc.abstractmethod
  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data: a byte string containing the compressed data.

    Returns:
      A tuple containing a byte string of the uncompressed data and
      the remaining compressed data.
    """
