# -*- coding: utf-8 -*-
"""The bzip2 decompressor object implementation."""

import bz2

from dfvfs.compression import decompressor
from dfvfs.compression import manager
from dfvfs.lib import definitions


class Bzip2Decompressor(decompressor.Decompressor):
  """Class that implements a BZIP2 decompressor using bz2."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_BZIP2

  def __init__(self):
    """Initializes the decompressor object."""
    super(Bzip2Decompressor, self).__init__()
    self._bz2_decompressor = bz2.BZ2Decompressor()

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data: a byte string containing the compressed data.

    Returns:
      A tuple containing a byte string of the uncompressed data and
      the remaining compressed data.
    """
    uncompressed_data = self._bz2_decompressor.decompress(compressed_data)
    remaining_compressed_data = getattr(
        self._bz2_decompressor, 'unused_data', b'')

    return uncompressed_data, remaining_compressed_data


# Register the decompressor with the compression manager.
manager.CompressionManager.RegisterDecompressor(Bzip2Decompressor)
