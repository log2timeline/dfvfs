# -*- coding: utf-8 -*-
"""The BZIP2 decompressor implementation."""

import bz2

from dfvfs.compression import decompressor
from dfvfs.compression import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class BZIP2Decompressor(decompressor.Decompressor):
  """BZIP2 decompressor using bz2."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_BZIP2

  def __init__(self):
    """Initializes a decompressor."""
    super(BZIP2Decompressor, self).__init__()
    self._bz2_decompressor = bz2.BZ2Decompressor()

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data (bytes): compressed data.

    Returns:
      tuple(bytes, bytes): uncompressed data and remaining compressed data.

    Raises:
      BackEndError: if the BZIP2 compressed stream cannot be decompressed.
    """
    try:
      uncompressed_data = self._bz2_decompressor.decompress(compressed_data)
      remaining_compressed_data = getattr(
          self._bz2_decompressor, 'unused_data', b'')

    except (EOFError, IOError) as exception:
      raise errors.BackEndError((
          f'Unable to decompress BZIP2 compressed stream with error: '
          f'{exception!s}.'))

    return uncompressed_data, remaining_compressed_data


manager.CompressionManager.RegisterDecompressor(BZIP2Decompressor)
