# -*- coding: utf-8 -*-
"""The LZMA and XZ decompressor implementations."""

import lzma

from lzma import LZMAError

from dfvfs.compression import decompressor
from dfvfs.compression import manager
from dfvfs.lib import definitions
from dfvfs.lib import errors


class XZDecompressor(decompressor.Decompressor):
  """XZ decompressor using lzma."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_XZ

  def __init__(self):
    """Initializes a decompressor."""
    super(XZDecompressor, self).__init__()
    # Note that lzma.FORMAT_XZ does not work for every implementation of lzma.
    self._lzma_decompressor = lzma.LZMADecompressor(1)

  def Decompress(self, compressed_data):
    """Decompresses the compressed data.

    Args:
      compressed_data (bytes): compressed data.

    Returns:
      tuple(bytes, bytes): uncompressed data and remaining compressed data.

    Raises:
      BackEndError: if the XZ compressed stream cannot be decompressed.
    """
    try:
      if hasattr(lzma, 'LZMA_VERSION'):
        # Note that we cannot use max_length=0 here due to different
        # versions of the lzma code.
        uncompressed_data = self._lzma_decompressor.decompress(
            compressed_data, 0)
      else:
        uncompressed_data = self._lzma_decompressor.decompress(compressed_data)

      remaining_compressed_data = getattr(
          self._lzma_decompressor, 'unused_data', b'')

    except (EOFError, IOError, LZMAError) as exception:
      raise errors.BackEndError((
          f'Unable to decompress XZ compressed stream with error: '
          f'{exception!s}.'))

    return uncompressed_data, remaining_compressed_data


class LZMADecompressor(XZDecompressor):
  """LZMA decompressor using lzma."""

  COMPRESSION_METHOD = definitions.COMPRESSION_METHOD_LZMA

  def __init__(self):
    """Initializes a decompressor."""
    super(LZMADecompressor, self).__init__()
    # Note that lzma.FORMAT_ALONE does not work for every implementation
    # of lzma.
    self._lzma_decompressor = lzma.LZMADecompressor(2)


manager.CompressionManager.RegisterDecompressors([
    LZMADecompressor, XZDecompressor])
